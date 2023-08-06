from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

"""
Tests relating generally to magic_folder.magic_file
"""

import io
import base64
import time
from mock import (
    patch,
)
from collections import (
    defaultdict,
)

from json import (
    dumps,
    loads,
)

from hyperlink import (
    DecodedURL,
)

from eliot import (
    start_action,
)
from eliot.twisted import (
    inline_callbacks,
)

from testtools.matchers import (
    MatchesAll,
    MatchesListwise,
    MatchesStructure,
    Always,
    Equals,
    LessThan,
    ContainsDict,
    AfterPreprocessing,
)
from testtools.twistedsupport import (
    succeeded,
    failed,
)
from hypothesis import (
    given,
    settings,
)
from hypothesis.stateful import (
    Bundle,
    RuleBasedStateMachine,
    rule,
    consumes,
    run_state_machine_as_test,
    multiple,
)
from hypothesis.strategies import (
    binary,
    floats,
    lists,
    builds,
)
from twisted.internet import reactor
from twisted.internet.task import (
    deferLater,
    Clock,
)
from twisted.internet.defer import (
    Deferred,
    inlineCallbacks,
    returnValue,
    succeed,
)
from twisted.python.filepath import (
    FilePath,
    IFilePath,
)
from treq.testing import (
    StubTreq,
    StringStubbingResource,
)
from zope.interface import (
    implementer,
)

from ..config import (
    create_testing_configuration,
)
from ..magic_folder import (
    MagicFolder,
)
from ..snapshot import (
    create_local_author,
    RemoteSnapshot,
    sign_snapshot,
    format_filenode,
    create_snapshot,
    write_snapshot_to_tahoe,
)
from ..status import (
    FolderStatus,
    WebSocketStatusService,
)
from ..tahoe_client import (
    create_tahoe_client,
)
from ..testing.web import (
    create_fake_tahoe_root,
    create_tahoe_treq_client,
)
from ..participants import (
    participants_from_collective,
    _WriteableParticipant,
)
from ..util.file import (
    PathState,
    get_pathinfo,
    seconds_to_ns,
)
from ..util.capabilities import (
    Capability,
)
from .common import (
    SyncTestCase,
    AsyncTestCase,
)
from .matchers import matches_flushed_traceback
from .strategies import (
    tahoe_lafs_immutable_dir_capabilities,
)
from ..magic_file import (
    MagicFileFactory,
    MagicFile,
)
from ..downloader import (
    RemoteSnapshotCacheService,
    InMemoryMagicFolderFilesystem,
    LocalMagicFolderFilesystem,
)
from ..uploader import (
    UploaderService,
    LocalSnapshotService,
    LocalSnapshotCreator,
)


# okay, so a "local-change" is really:
# - wait X
# - write the data locally
# - wait Y
# - "let" the scanner discover it ... i.e. inject local-change
# - wait Z
# - inject "remote-change" event to other side (if "two person")


# so a "single device" machine does't _really_ make sense as a test
# (because the only kind of conflict there is "some other process
# messed with a file at the right moment") ... but we'll only have one
# "real" device with a MagicFile state-machine and inject "fake
# "remote-update" events.

#
# hmmmm .. can we completely fake out the filesystem?  (although that
# might be a better unit-test, I actually _do_ want to test out the
# "real" filesystem ... so maybe this is where we want a fake?  that
# is: we have "a filesystem API" .. with 3 implementations: in-memory,
# unix (linux+mac), and windows.
#
# then, we test that the in-memory one works the same as "unix" and
# "windows"? (so maybe we want two in-emory fakes: one that "works
# like windows" and one that "works like unix-y")

# so, we can have two kinds of changes:
# local-change:
#  - wait X
#  - write data locally
#  - wait Y
#  - inject _local_change() to state-machine
#  - (wait for personal-dmd-update? -> at least need to record _when_ it happened)
# remote-change:
#  - wait X
#  - (change fake tahoe/remote-dmd?)
#  - inject _remote_update
#  - (wait for personal-dmd-update? -> record it at least)

# post-hoc, we can analyze the timeline and answer:
#  - what is the state of the local filesystem (i.e. what _should_ its contents be)
#    - (_can_ we, always? even those 'last second' conflicts??)
#  - does it match (e.g. expected conflicts, etc)
#  - (all we care about in the timeline is relative position .. right?)


@implementer(IFilePath)
class FakeFilePath:
    """
    """
    def __init__(self, fs, name, isdir=None, content=None):
        self.fs = fs
        self.name = name
        self._isdir = isdir  # None = "dunno yet" / nonexistant
        self._data = None
        if isdir:
            assert content is None, "content must be None for directories"

    def child(self, name):
        return FakeFilePath(self.fs, self.name + "/" + name)

    def makedirs(self):
        assert self._isdir is None or self._isdir, "already a file"

    def open(self, mode):
        assert self._isdir is not None and not self._isdir, "not a file"
        self._data = io.BytesIO()
        self._ctime = self.fs._clock.seconds()
        self._mtime = self.fs._clock.seconds()
        # XXX for proper mtime i guess we'd have to wrap the BytesIO write()??
        return self._data


class FakeFilesystem:
    """
    An in-memory, fake filesystem. Only works with FilePath API.

    Is there really no library for this?

    Should this also implement the 'downloader' side? (i.e. IMagicFolderFilesystem?)
    """

    def __init__(self, clock):
        self._root = defaultdict(dict)
        self._clock = clock

    def add_entry(self, name):
        segments = name.split("/")
        location = self.root
        for s in segments[:-1]:
            location = location[s]
        assert not location.haskey(segments[-1]), "already have entry"
        p = location[segments[-1]] = FakeFilePath(self, name)
        return p

    def get_entry(self, name):
        segments = name.split("/")
        thing = self.root
        for s in segments:
            thing = thing[s]
        if not isinstance(thing, FakeFilePath):
            raise KeyError(name)
        return thing


class FakeLocalSnapshotService:
    """
    Synchronous / instant fake of (most of) the local snapshot creator
    """

    def __init__(self, filesystem, mfconfig):
        """
        :param FakeFilesystem filesystem: pretend filesystem
        """
        self._fs = filesystem
        self._mfconfig = mfconfig
        self._snaps = dict()

    def add_file(self, path):
        # XXX so _snaps should be _de-populated_ of this "path" once
        # we upload it .. so i guess the fake-uploader takes snaps
        # _out_ of this thing and "pretends to upload" them
        existing = self._snaps.get(path, None)
        try:
            f = self._fs.get_entry(path)
        except KeyError:
            # must be delete? (no entry)
            f = None
        now = self._fs._clock.seconds()
        self._snaps[path] = LocalSnapshot(
            relpath=path,
            author=self._author,
            metadata={
                "mtime": None if f is None else f._mtime,
                "ctime": now,
            },
            content_path=f,
            parents_local=[existing] if existing else [],
            parents_remote=[], # XXX uploader does: self._db.get_remotesnapshot(relpath)

        )
        # XXX we're supposed to write this to the database too, right?
        return succeed(self._snaps[path])


class FakeUploader:
    """
    Synchronous / instant fake of (most of) the uploader
    """

    def __init__(self, mfconfig, snapshotter):
        self._config = mfconfig
        self._snapshotter = snapshotter


class SingleDeviceStateMachineExplorer(RuleBasedStateMachine):
    """
    """

    def __init__(self, case):
        super().__init__()
        self.case = case
        from twisted.internet import reactor
        self._clock = Clock()
        # actual timeline of events
        self._timeline = []
        self._events = []
        self._deferreds = []
        self._basedir = FilePath(self.case.mktemp())
        self._basedir.makedirs()
        self._nodedir = FilePath(self.case.mktemp())  # grrrr
        self._nodedir.makedirs()
        self._stashdir = FilePath(self.case.mktemp())  # grrrr
        self._stashdir.makedirs()
        self._magicdir = FilePath(self.case.mktemp())  # grrrr
        self._magicdir.makedirs()

        self._config = create_testing_configuration(
            self._basedir,
            self._nodedir,
        )
        self._root = create_fake_tahoe_root()
        self._tahoe_client = create_tahoe_client(
            DecodedURL.from_text("http://.example.invalid/v1/"),
            create_tahoe_treq_client(root=self._root),
        )

        _, self._collective_dmd_raw = self._root.add_data(
            "URI:DIR2:",
            dumps([
                "dirnode",
                {
                    "children": {}
                },
            ]).encode("utf8"),
        )
        self._collective_dmd = Capability.from_string(self._collective_dmd_raw)

        _, self._personal_dmd_raw = self._root.add_data(
            "URI:DIR2:",
            dumps([
                "dirnode",
                {
                    "children": {}
                },
            ]).encode("utf8"),
        )
        self._personal_dmd = Capability.from_string(self._personal_dmd_raw)

        self._status = WebSocketStatusService(
            self._clock,
            self._config,
        )
        self._author = create_local_author("ava")
        self._mfconfig = self._config.create_magic_folder(
            "folder_name",
            self._magicdir,
            self._author,
            self._collective_dmd,
            self._personal_dmd,
            60,
            60,
        )
        self._folder_status = FolderStatus(
            "folder_name",
            self._status,
        )
        self._filesystem = FakeFilesystem(self._clock)
        self._local_snapshot_service = FakeLocalSnapshotService(self._filesystem, self._mfconfig)
        self._uploader = FakeUploader(
            self._mfconfig,
            self._local_snapshot_service,
        )
        self._write_participant = _WriteableParticipant(
            self._personal_dmd,
            self._tahoe_client,
        )
        self._remote_cache = RemoteSnapshotCacheService(
            self._mfconfig,
            self._tahoe_client,
        )
        self._magic_fs = LocalMagicFolderFilesystem(
            self._magicdir,
            self._stashdir,
        )

        self._factory = MagicFileFactory(
            self._config,
            self._tahoe_client,
            self._folder_status,
            self._local_snapshot_service,
            self._uploader,
            self._write_participant,
            self._remote_cache,
            self._magic_fs,
            synchronous=False,  # we want to use the reactor
        )
        self._action = start_action(action_type="test")
        self._magic_file = MagicFile(
            self._magicdir.child("dummy"),
            "dummy",
            self._factory,
            self._action,
        )

    ava_events = Bundle("ava_events")

    def _sleep(self, seconds):
        d = Deferred()
        self._clock.callLater(seconds, d.callback, None)
        return d

    @rule(
        target=ava_events,
        content=binary(),
        wait0=floats(min_value=0, max_value=100.0),
        wait1=floats(min_value=0, max_value=100.0),
    )
    def ava_local_change(self, content, wait0, wait1):
        return (
            self.perform_ava_local_change,
            content, wait0, wait1,
        )

    @inlineCallbacks
    def perform_ava_local_change(self, content, wait0, wait1):
        # not doing a deferred wait here allows "0" to mean "do
        # the thing right away"
        if wait0 > 0:
            yield self._sleep(wait0)
        self._timeline.append((self._clock.seconds(), "write-local"))
        with self._magicdir.child("dummy").open("w") as f:
            f.write(content)
        # same as above, allow Hypothesis to try "right away" when
        # waits[x] == 0.0
        if wait1 > 0:
            yield self._sleep(wait1)
        self._timeline.append((self._clock.seconds(), "create-update"))
        yield self._magic_file.create_update()
        self._timeline.append((self._clock.seconds(), "update-created"))
        yield self._magic_file.finish()
        self._timeline.append((self._clock.seconds(), "update-completed"))

    @rule(event=ava_events)
    def perform_event(self, event):
        print("DING", event, type(event))
        f, content, wait0, wait1 = event
        try:
            d = f(content, wait0, wait1)
            d.addErrback(print)
            self._deferreds.append(d)
            print("DDD", d)
        except Exception as e:
            print("QQQ", e)
        print("ZZZ", d)
        print(self.case)
        self.case.assertThat(
            succeeded(d),
            Always()
        )
        print("ZZZ2", d)

    def teardown(self):
        print("teardown", len(self._deferreds))
        for x in self._deferreds:
            print("YYY", x)
        for s, e in self._timeline:
            print("  ", s, e)


class TwoDeviceStateMachineExplorer(RuleBasedStateMachine):
    """
    """

    def __init__(self, case):
        super().__init__()
        self.case = case
        self._timer = 0.0
        self._timeline = []

    ava_events = Bundle("ava_events")
    bob_events = Bundle("bob_events")

    def _next_time(self):
        t = self._timer
        self._timer += 1.0
        return t

    @rule(target=ava_events)
    def ava_local_change(self, content=binary()):
        return ("local-change", content)

    @rule(target=bob_events)
    def bob_local_change(self, content=binary()):
        return ("local-change", content)

    @rule(event=bob_events)
    def perform_bob(self, event):
        self._timeline.append((self._next_time(), event))

    @rule(event=ava_events)
    def perform_ava(self, event):
        self._timeline.append((self._next_time(), event))

    @rule()
    def confirm_timeline(self):
        self.case.assertThat(
            len(self._timeline),
            LessThan(10)
        )

    def teardown(self):
        print("teardown")


class Tests(AsyncTestCase):
    """
    the built-in hypothesis machinery doesn't support trial, so we
    have to hack around that.
    """
    def test_machine(self):
        """
        """
        # XXX fixme
        state_settings = settings(max_examples=2)
        run_state_machine_as_test(
            lambda: SingleDeviceStateMachineExplorer(self),
            settings=state_settings,
        )
