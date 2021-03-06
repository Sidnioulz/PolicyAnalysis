import unittest
from Application import Application
from UserConfigLoader import UserConfigLoader
from File import File, EventFileFlags
from LibraryManager import LibraryManager

class TestLibraryManager(unittest.TestCase):
    def setUp(self):
        pass
        self.userConf = UserConfigLoader.get("user.ini")
        self.mgr = LibraryManager.get()

    def test_pol_load_app_conf(self):
        app = Application("ristretto.desktop", pid=21, tstart=0, tend=300)
        file = File("/home/user/Images/sample.jpg", 140, 0, "image/jpeg")
        file.addAccess(app, 140, EventFileFlags.create | EventFileFlags.read)

        res = self.mgr.getAppPolicy(app, libMod=LibraryManager.Default)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "image")

    def test_library_roots(self):

        roots = self.mgr.getAllLibraryRoots(libMod=LibraryManager.Custom)
        self.assertEqual(len(roots), 11)
        self.assertIn("/media/user", roots)
        self.assertIn("/home/user/Desktop", roots)
        self.assertIn("/home/user/Downloads", roots)
        self.assertIn("/home/user/Documents", roots)
        self.assertIn("/home/user/Images", roots)
        self.assertIn("/home/user/Music", roots)
        self.assertIn("/home/user/Videos", roots)
        self.assertIn("/home/user/.config", roots)
        self.assertIn("/home/user/.cache", roots)
        self.assertIn("/home/user/.local/share", roots)
        self.assertIn("/home/user", roots)

        roots = self.mgr.getAllLibraryRoots(libMod=LibraryManager.Custom,
                                            addXdgRoots=False)
        self.assertEqual(len(roots), 7)
        self.assertIn("/media/user", roots)
        self.assertIn("/home/user/Desktop", roots)
        self.assertIn("/home/user/Downloads", roots)
        self.assertIn("/home/user/Documents", roots)
        self.assertIn("/home/user/Images", roots)
        self.assertIn("/home/user/Music", roots)
        self.assertIn("/home/user/Videos", roots)

        roots = self.mgr.getAllLibraryRoots(libMod=LibraryManager.Default,
                                            addXdgRoots=False)
        self.assertEqual(len(roots), 5)
        self.assertIn("/media/user", roots)
        self.assertIn("/home/user/Documents", roots)
        self.assertIn("/home/user/Images", roots)
        self.assertIn("/home/user/Music", roots)
        self.assertIn("/home/user/Videos", roots)

    def tearDown(self):
        pass
        self.userConf = None
