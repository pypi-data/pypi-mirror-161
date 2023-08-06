"""zhinst-toolkit AWG node adaptions."""
import json
import logging
import time
import typing as t

from zhinst.toolkit.driver.nodes.command_table_node import CommandTableNode
from zhinst.toolkit.nodetree import Node, NodeTree
from zhinst.toolkit.nodetree.helper import (
    lazy_property,
    create_or_append_set_transaction,
)
from zhinst.toolkit.waveform import Waveforms

logger = logging.getLogger(__name__)

if t.TYPE_CHECKING:
    from zhinst.toolkit.session import Session


class AWG(Node):
    """AWG node.

    This class implements the basic functionality for the device specific
    arbitrary waveform generator.
    Besides the upload/compilation of sequences it offers the upload of
    waveforms and command tables.

    Args:
        root: Root of the nodetree
        tree: Tree (node path as tuple) of the current node
        session: Underlying session.
        serial: Serial of the device.
        index: Index of the corresponding awg channel
        device_type: Device type
    """

    def __init__(
        self,
        root: NodeTree,
        tree: tuple,
        session: "Session",
        serial: str,
        index: int,
        device_type: str,
    ):
        Node.__init__(self, root, tree)
        self._session = session
        self._serial = serial
        self._index = index
        self._device_type = device_type

    def enable_sequencer(self, *, single: bool) -> None:
        """Starts the sequencer of a specific channel.

        Waits until the sequencer is enabled.

        Args:
            single: Flag if the sequencer should be disabled after finishing
            execution.
        """
        self.single(single)
        self.enable(1, deep=True)
        self.enable.wait_for_state_change(1)

    def wait_done(self, *, timeout: float = 10, sleep_time: float = 0.005) -> None:
        """Wait until the AWG is finished.

        Args:
            timeout: The maximum waiting time in seconds for the generator
                (default: 10).
            sleep_time: Time in seconds to wait between requesting generator
                state

        Raises:
            RuntimeError: If continuous mode is enabled
            TimeoutError: If the sequencer program did not finish within
                the specified timeout time
        """
        if not self.single():
            raise RuntimeError(
                f"{repr(self)}: The generator is running in continuous mode, "
                "it will never be finished."
            )
        try:
            self.enable.wait_for_state_change(0, timeout=timeout, sleep_time=sleep_time)
        except TimeoutError as error:
            raise TimeoutError(
                f"{repr(self)}: The execution of the sequencer program did not finish "
                f"within the specified timeout ({timeout}s)."
            ) from error

    def load_sequencer_program(
        self, sequencer_program: str, *, timeout: float = 100.0
    ) -> None:
        """Compiles the given sequencer program on the AWG Core.

        Args:
            sequencer_program: Sequencer program to be uploaded.
            timeout: Maximum time to wait for the compilation on the device in
                seconds.

        Raises:
            ValueError: `sequencer_program` is an empty string.
            TimeoutError: If the upload or compilation times out.
            RuntimeError: If the upload or compilation failed.

        .. versionadded:: 0.3.4

            `sequencer_program` does not accept empty strings

        """
        if not sequencer_program:
            raise ValueError("Empty sequencer program not allowed.")
        awg = self._session.modules.create_awg_module()
        raw_awg = awg.raw_module
        awg.device(self._serial)
        awg.index(self._index)
        if "SHFQC" in self._device_type:
            awg.sequencertype("sg")
        raw_awg.execute()
        logger.info(f"{repr(self)}: Compiling sequencer program")
        awg.compiler.sourcestring(sequencer_program)
        compiler_status = awg.compiler.status()
        start = time.time()
        while compiler_status == -1:
            if time.time() - start >= timeout:
                logger.critical(f"{repr(self)}: Program compilation timed out")
                raise TimeoutError(f"{repr(self)}: Program compilation timed out")
            time.sleep(0.1)
            compiler_status = awg.compiler.status()

        if compiler_status == 1:
            logger.critical(
                f"{repr(self)}: Error during sequencer compilation"
                f"{awg.compiler.statusstring()}"
            )
            raise RuntimeError(
                f"{repr(self)}: Error during sequencer compilation."
                "Check the log for detailed information"
            )
        if compiler_status == 2:
            logger.warning(
                f"{repr(self)}: Warning during sequencer compilation"
                f"{awg.compiler.statusstring()}"
            )
        if compiler_status == 0:
            logger.info(f"{repr(self)}: Compilation successful")

        progress = awg.progress()
        logger.info(f"{repr(self)}: Uploading ELF file to device")
        while progress < 1.0 or awg.elf.status() == 2 or self.ready() == 0:
            if time.time() - start >= timeout:
                logger.critical(f"{repr(self)}: Program upload timed out")
                raise TimeoutError(f"{repr(self)}: Program upload timed out")
            logger.info(f"{repr(self)}: {progress*100}%")
            time.sleep(0.1)
            progress = awg.progress()

        if awg.elf.status() == 0 and self.ready():
            logger.info(f"{repr(self)}: ELF file uploaded")
        else:
            logger.critical(
                f"{repr(self)}: Error during upload of ELF file"
                f"(with status {awg.elf.status()}"
            )
            raise RuntimeError(
                f"{repr(self)}: Error during upload of ELF file."
                "Check the log for detailed information"
            )

    def write_to_waveform_memory(
        self, waveforms: Waveforms, indexes: list = None, validate: bool = True
    ) -> None:
        """Writes waveforms to the waveform memory.

        The waveforms must already be assigned in the sequencer program.

        Args:
            waveforms: Waveforms that should be uploaded.
            indexes: Specify a list of indexes that should be uploaded. If
                nothing is specified all available indexes in waveforms will
                be uploaded. (default = None)
            validate: Enable sanity check preformed by toolkit, based on the
                waveform descriptors on the device. Can be disabled for e.g.
                speed optimizations. Does not affect the checks happen in LabOne
                and or the firmware. (default = True)

        Raises:
            IndexError: The index of a waveform exceeds the one on the device
                and `validate` is True.
            RuntimeError: One of the waveforms index points to a
                filler(placeholder) and `validate` is True.
        """
        waveform_info = None
        num_waveforms = None
        if validate:
            waveform_info = json.loads(self.waveform.descriptors()).get("waveforms", [])
            num_waveforms = len(waveform_info)
        with create_or_append_set_transaction(self._root):
            for waveform_index in waveforms.keys():
                if indexes and waveform_index not in indexes:
                    continue
                if num_waveforms is not None and waveform_index >= num_waveforms:
                    raise IndexError(
                        f"There are {num_waveforms} waveforms defined on the device "
                        "but the passed waveforms specified one with index "
                        f"{waveform_index}."
                    )
                if (
                    waveform_info
                    and "__filler" in waveform_info[waveform_index]["name"]
                ):
                    raise RuntimeError(
                        f"The waveform at index {waveform_index} is only "
                        "a filler and can not be overwritten"
                    )
                self.root.transaction.add(
                    self.waveform.waves[waveform_index],
                    waveforms.get_raw_vector(
                        waveform_index,
                        target_length=int(waveform_info[waveform_index]["length"])
                        if waveform_info
                        else None,
                    ),
                )

    def read_from_waveform_memory(self, indexes: t.List[int] = None) -> Waveforms:
        """Read waveforms to the waveform memory.

        Args:
            indexes: List of waveform indexes to read from the device. If not
                specified all assigned waveforms will be downloaded.

        Returns:
            Waveform object with the downloaded waveforms.
        """
        nodes = [self.waveform.descriptors.node_info.path]
        if indexes is not None:
            for index in indexes:
                nodes.append(self.waveform.node_info.path + f"/waves/{index}")
        else:
            nodes.append(self.waveform.waves["*"].node_info.path)
        nodes_str = ",".join(nodes)
        waveforms_raw = self._session.daq_server.get(
            nodes_str, settingsonly=False, flat=True
        )
        waveform_info = json.loads(
            waveforms_raw.pop(self.waveform.descriptors.node_info.path)[0]["vector"]
        ).get("waveforms", [])
        waveforms = Waveforms()
        for node, waveform in waveforms_raw.items():
            slot = int(node[-1])
            if "__filler" not in waveform_info[slot]["name"]:
                waveforms.assign_native_awg_waveform(
                    slot,
                    waveform[0]["vector"],
                    channels=int(waveform_info[slot].get("channels", 1)),
                    markers_present=bool(
                        int(waveform_info[slot].get("marker_bits")[0])
                    ),
                )
        return waveforms

    @lazy_property
    def commandtable(self) -> t.Optional[CommandTableNode]:
        """Command table module."""
        if self["commandtable"].is_valid():
            return CommandTableNode(
                self._root, self._tree + ("commandtable",), self._device_type
            )
        return None
