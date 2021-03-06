"""A runtime instance of a Linux Desktop application."""
from xdg import DesktopEntry
from constants import DESKTOPPATHS, DESKTOPIDRE
from blist import sortedlist
from copy import deepcopy
import re
import os


class Application(object):
    """A runtime instance of a Linux Desktop application.

    Representation of a UNIX process, along with information on the Desktop
    application it is expected to belong to (using XDG Desktop Specification).
    Applications are identified by their XDG Desktop identifier, or by the path
    to their executable.
    """

    """
    init = False              # type: bool
    entry = None              # type: DesktopEntry
    desktopid = None          # type: str; final id of the app after init
    interpreterid = None      # type: str; id of interpreter, e.g. java, python
    path = None               # type: str; path to executable
    pid = 0                   # type: int; UNIX process ID
    tstart = 0                # type: int; when the app is known to exist
    tend = 0                  # type: int; when it's known to cease existing
    cmdline = ''              # type: str; complete command line, when known
    events = []               # type: list
    fds = []               # type: list
    # windows = []              # type: list
    # documents = []            # type: list
    # states = []               # type: list
    # uris = []                 # type: list
    # ipc = []                  # type: list
    # parent = None             # type: Application
    # children = []             # type: list
    """

    desktopre = re.compile(DESKTOPIDRE)
    desktopCache = dict()

    def __init__(self,
                 desktopid: str=None,
                 path: str=None,
                 pid: int=0,
                 tstart: int=0,
                 tend: int=0,
                 interpreterid: str=None):
        """Construct an Application, using a desktopid or a path."""
        super(Application, self).__init__()
        self.clearEvents()
        self.clearFDs()

        self.desktopid = None
        self.cmdline = None
        self.path = None

        if desktopid:
            self.desktopid = desktopid.lower()
            self.__initFromDesktopID()
        elif path:
            self.path = path
            self.__initFromPath()
        else:
            raise ValueError("A binary path or a Desktop id are needed to "
                             "instantiate an Application.")

        self.pid = pid
        self.tstart = tstart
        self.tend = tend
        self.interpreterid = interpreterid.lower() if interpreterid else None
        self._uid = None
        self._regenUid()

    @staticmethod
    def __getDesktopFile(desktopid: str):
        """Get a .desktop file from the desktop cache for a given desktopid."""
        finalid = None
        if not Application.desktopCache.get(desktopid):
            de = DesktopEntry.DesktopEntry()
            for path in DESKTOPPATHS:
                if not desktopid.endswith(".desktop"):
                    depath = os.path.realpath(path + desktopid + ".desktop")
                else:
                    depath = os.path.realpath(path + desktopid)
                try:
                    de.parse(depath)
                except(DesktopEntry.ParsingError) as e:
                    pass
                else:
                    res = Application.desktopre.match(depath)
                    try:
                        finalid = res.groups()[0].lower()
                    except(ValueError, KeyError) as e:
                        finalid = depath.lower()
                    break

            Application.desktopCache[finalid] = (finalid, de)
            return (finalid, de)

        return Application.desktopCache.get(desktopid)

    @staticmethod
    def getDesktopIdFromDesktopUri(uri: str):
        """Calculate the Application Desktop Id for a given URI."""
        if not uri:
            return (None, None)

        defile = uri[14:] if uri.startswith("application://") else uri
        return Application.__getDesktopFile(defile)

    def __initFromDesktopID(self):
        """Initialise an application using an XDG desktop identifier."""
        (did, entry) = Application.getDesktopIdFromDesktopUri(self.desktopid)

        if not did:
            # TODO get path from Exec/TryExec for de entry
            raise ValueError("Could not initialise desktopid '%s'" %
                             self.desktopid)
        else:
            self.desktopid = did
            self.init = True

    # def __eq__(self, other):
    #     """Tell if an Application is equal to another (same UID)."""
    #     if isinstance(other, self.__class__):
    #         return self.tstart == other.tstart and \
    #                 self.pid == other.pid # and \
    #                 # self.desktopid == other.desktopid
    #     return False

    # def __ne__(self, other):
    #     """Tell if an Application differs from another (different UIDs)."""
    #     return not self.__eq__(other)

    def __hash__(self):
        """Tell if an Application differs from another (different UIDs)."""
        return self._uid.__hash__()

    def isInitialised(self):
        """Check if an Application is initialised."""
        return self.init

    def getDesktopId(self):
        """Return the Application's .desktop entry identifier."""
        return self.desktopid

    def getInterpreterId(self):
        """Return the Application's interpreter .desktop id if it exists."""
        return self.interpreterid

    def _regenUid(self):
        """Regenerate the UID for this application."""
        self._uid = "%s:%d:%d" % (self.desktopid, self.pid, self.tstart)

    def uid(self):
        """Generate a unique string identifier for this Application."""
        return self._uid

    def hasSameDesktopId(self, other, resolveInterpreter: bool=False):
        """Check whether a desktop id is equivalent to the current object's.

        other -- either another Application or a string containing the desktop
        id to compare.
        resolveInterpreter -- also compare interpreterid, in which case only
        Application instances can be given to :other: (default False).
        """
        if hasattr(other, 'desktopid') and hasattr(other, 'interpreterid'):
            otherId = other.desktopid
            otherInterpreter = other.interpreterid
        elif resolveInterpreter:
            raise AttributeError("This function can only resolve interpreters "
                                 "if you pass it an Application instance, not "
                                 "a string.")
        else:
            otherId = other.lower()

        try:
            res = Application.desktopre.match(otherId)
            otherName = res.groups()[0]
        except (ValueError, KeyError) as e:
            return False
        else:
            if self.desktopid == otherName:
                return True
            elif resolveInterpreter and self.interpreterid == otherName:
                return True
            elif resolveInterpreter and self.desktopid == otherInterpreter:
                return True
            else:
                return False

    def getPid(self):
        """Return the Application's pid."""
        return self.pid

    def getTimeOfStart(self):
        """Return the Application's time of start."""
        return self.tstart

    def getTimeOfEnd(self):
        """Return the Application's time of end."""
        return self.tend

    def setTimeOfStart(self, val):
        """Set the Application's time of start to the passed value."""
        self.tstart = val

    def setTimeOfEnd(self, val):
        """Set the Application's time of end to the passed value."""
        self.tend = val

    def merge(self, other):
        """Merge another Application with the current one.

        Both Applications must have the same PID and initialisation status, and
        an equivalent Desktop id (or the interpreterid of one Application must
        be equal to the other's desktopid). The merged Application will take
        any parameters from :other: that it was missing, and will also update
        its times of start and end to cover the period when both instances were
        running.
        """
        if not isinstance(other, Application):
            raise TypeError("Only other Application instances can be merged.")

        if self.init != other.init:
            raise ValueError("Initialised Applications cannot be merged with "
                             "uninitialised ones.")

        if self.pid != other.pid:
            raise ValueError("Only Applications with the same PID can be "
                             "merged.")

        if self.desktopid != other.desktopid:
            if self.interpreterid == other.desktopid:
                pass
            elif self.desktopid == other.interpreterid:
                self.desktopid = other.desktopid
                self._regenUid()
                self.interpreterid = other.interpreterid
                pass
            else:
                raise ValueError("Only Applications with the same Desktop id "
                                 "can be merged.")

        if (not self.path) and other.path:
            self.path = other.path
        if (not self.cmdline) and other.cmdline:
            self.cmdline = other.cmdline

        self.setTimeOfStart(min(other.getTimeOfStart(),
                                self.getTimeOfStart()))
        self.setTimeOfEnd(max(other.getTimeOfEnd(),
                              self.getTimeOfEnd()))
        self.events.update(list(set(other.events) - set(self.events)))

        self._regenUid()
        return self

    def setCommandLine(self, cmd):
        """Set the command line used to start this Application."""
        self.cmdline = cmd

    def getCommandLine(self):
        """Return the command line used to start this Application."""
        return self.cmdline

    def clearEvents(self):
        """Clear all events to be modelled for this Application."""
        self.events = sortedlist(key=lambda i: i.time)

    def openFD(self, fd: int, path: str, time: int):
        """Add a file descriptor opened by this Application."""
        fdList = self.fds.get(fd) or []

        # FD duplication can lead to us having to loop resolutions
        if path.startswith('@'):
            from FileFactory import FileFactory
            fc = FileFactory.get()
            resolved = fc.resolveFDRef(path, time)
            path = resolved or path

        # Sanity check, last should be before us.
        if len(fdList) > 0:
            if fdList[-1][2] and fdList[-1][2] > time:
                print("Error: Attempt to open file "
                      "descriptor %d for File '%s' in Application '%s', but "
                      "there is already an open file descriptor with this "
                      "number." % (fd, path, self.uid()))

        # Path, time of opening, time of closing
        fdList.append((path, time, 0))
        self.fds[fd] = fdList

    def closeFD(self, fd: int, time: int):
        """Close a file descriptor open by this Application."""
        fdList = self.fds.get(fd) or None

        if fdList:
            last = fdList[-1]

            # Sanity check, last should be currently open, or else we missed a
            # new FD opening.
            if last[2] == 0:
                last = (last[0], last[1], time)
                fdList[-1] = last
                self.fds[fd] = fdList
            # else:
            #     print("Info: Attempt to close fd %d in Application '%s', but"
            #           " it has already been closed. We must've missed a new"
            #           " fd opening event." % (fd, self.uid()))

        # else:
        #     print("Info: Application '%s' received an event closing fd %d, "
        #           "which wasn't opened. This is most likely because a system"
        #           " call was not collected." % (self.uid(), fd))

    def resolveFD(self, fd: int, time: int):
        """Resolve a file descriptor reference for a given fd and time."""
        fds = self.fds.get(fd)
        if not fds:
            print("Info: could not resolve fd '%d' for Application '%s'" % (
                   fd, self.uid()))
            return None

        for (path, tstart, tend) in fds:
            if time >= tstart and (not tend or time <= tend):
                return path
        else:
            return None

    def clearFDs(self):
        """Clear all fds opened by this Application."""
        self.fds = dict()

    def getSetting(self,
                   key: str,
                   group: str='Desktop Entry',
                   defaultValue=None,
                   type: str="string"):
        """Get a stored setting relative to this app."""
        (__, entry) = Application.desktopCache.get(self.desktopid)

        if not entry:
            return None

        isList = False
        if type.endswith(" list"):
            isList = True
            type = type[:-5]
            defaultValue = [] if defaultValue is None else defaultValue

        return entry.get(key,
                         group=group,
                         type=type,
                         list=isList) or defaultValue

    def getAppType(self):
        """Return the type of the Appplication (sys/desktop/study/userland)."""
        t = self.getSetting('Type')
        if not t:
            raise ValueError("Application %s has no type." % self.uid())
        return t

    def isSystemApp(self):
        """Tell if the Application is a system daemon or service."""
        t = self.getSetting('Type')
        if not t:
            raise ValueError("Application %s has no type." % self.uid())
        return t == 'System'

    def isDesktopApp(self):
        """Tell if the Application is a Desktop service or component."""
        t = self.getSetting('Type')
        if not t:
            raise ValueError("Application %s has no type." % self.uid())
        return t == 'Desktop'

    def isStudyApp(self):
        """Tell if the Application is a process used for data collection."""
        t = self.getSetting('Type')
        if not t:
            raise ValueError("Application %s has no type." % self.uid())
        return t == 'Study'

    def isUserlandApp(self):
        """Tell if the Application is an actual app (not sys/desktop/study)."""
        t = self.getSetting('Type')
        if not t:
            raise ValueError("Application %s has no type." % self.uid())
        return t == 'Application'

    def split(self, beforeEnd: int, afterStart: int):
        """Split this into two Applications, with their distinct Events.

        Split this Application into an Application starting at the same time,
        and ending at :beforeEnd:, and an Application starting at :afterStart:
        and ending at this Application's end time. Events are split too. If
        Events exist in the gap between :beforeEnd: and :afterStart:, this
        function returns an IndexError.
        """
        from Event import Event
        il = self.events.bisect_left(Event(time=beforeEnd))
        ir = self.events.bisect_right(Event(time=afterStart))
        if il != ir:
            raise IndexError("Cannot split Application '%s' that contains "
                             "%d events between the runtimes of the two "
                             "resulting Applications (between %s and %s)." % (
                              self.uid(), ir - il, beforeEnd, afterStart))

        appLeft = deepcopy(self)
        appLeft.events = self.events[:il]
        if len(appLeft.events):
            appLeft.tend = appLeft.events[-1].time

        appRight = deepcopy(self)
        appRight.events = self.events[ir:]
        if len(appRight.events):
            appRight.tstart = appRight.events[0].time

        return (appLeft, appRight)

    def addEvent(self, event: 'Event'):
        """Keep an Event temporarily till its final actor is resolved."""
        self.events.add(event)

    def sendEventsToStore(self):
        """Send this app's Events to the EventStore, and clear them."""
        # Get the EventStore
        from EventStore import EventStore
        eventStore = EventStore.get()

        # Send each Event, after updating it to point to the updated self.
        for event in self.events:
            event.actor = self
            eventStore.append(event)

        # Clear events, to save RAM.
        self.clearEvents()
