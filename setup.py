# A setup script showing how to extend py2exe.
#
# In this case, the py2exe command is subclassed to create an installation
# script for InnoSetup, which can be compiled with the InnoSetup compiler
# to a single file windows installer.
#
# By default, the installer will be created as dist\Output\setup.exe.

from distutils.core import setup
import py2exe
import sys
import glob
import os

class InnoScript:
    def __init__(self,
                 name,
                 lib_dir,
                 dist_dir,
                 windows_exe_files,
                 lib_files,
                 version):
        self.lib_dir = lib_dir
        self.dist_dir = dist_dir
        if not self.dist_dir[-1] in "\\/":
            self.dist_dir += "\\"
        self.name = name
        self.version = version
        self.windows_exe_files = [self.chop(p) for p in windows_exe_files]
        self.lib_files = [self.chop(p) for p in lib_files]

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir):]
    
    def create(self, pathname):
        self.pathname = pathname
        ofi = self.file = open(pathname, "w")
        print >> ofi, "; WARNING: This script has been created by py2exe. Changes to this script"
        print >> ofi, "; will be overwritten the next time py2exe is run!"
        print >> ofi, r"[Setup]"
        print >> ofi, r"AppName=%s" % self.name
        print >> ofi, r"AppVerName=%s %s" % (self.name, self.version)
        print >> ofi, r"DefaultDirName={pf}\%s" % self.name
        print >> ofi, r"DefaultGroupName=%s" % self.name
        print >> ofi, r"Compression=lzma/max"
        print >> ofi

        print >> ofi, r"[Files]"
        for path in self.windows_exe_files + self.lib_files:
            print >> ofi, r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (path, os.path.dirname(path))
        print >> ofi

        print >> ofi, r"[Icons]"
        for path in self.windows_exe_files:
            print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\%s"' % \
                  (self.name, path)
        print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"' % self.name

    def compile(self):
        try:
            import ctypes
        except ImportError:
            try:
                import win32api
            except ImportError:
                import os
                os.startfile(self.pathname)
            else:
                print "Ok, using win32api."
                win32api.ShellExecute(0, "compile",
                                                self.pathname,
                                                None,
                                                None,
                                                0)
        else:
            print "Cool, you have ctypes installed."
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                                                      self.pathname,
                                                      None,
                                                      None,
                                                      0)
            if res < 32:
                raise RuntimeError, "ShellExecute failed, error %d" % res


################################################################

from py2exe.build_exe import py2exe

class build_installer(py2exe):
    # This class first builds the exe file(s), then creates a Windows installer.
    # You need InnoSetup for it.
    def run(self):
        # First, let py2exe do it's work.
        py2exe.run(self)

        lib_dir = self.lib_dir
        dist_dir = self.dist_dir
##         for key in dir(self.distribution.metadata):
##             print key, getattr(self.distribution.metadata, key)
        
        # create the Installer, using the files py2exe has created.
        script = InnoScript(self.distribution.metadata.name,
                            lib_dir,
                            dist_dir,
                            self.windows_exe_files,
                            self.lib_files,
                            self.distribution.metadata.version)
        print "*** creating the inno setup script***"
        script.create("%s\\%s.iss" % (dist_dir, self.distribution.metadata.name))
        print "*** compiling the inno setup script***"
        script.compile()
        # Note: By default the final setup.exe will be in an Output subdirectory.

################################################################
################################################################
exclude_win = [ 'AppKit', 'Foundation', 'objc' ] # mac stuff not needed on windows
dll_win = [ 'msvcr71.dll' ]

kw95 = dict(options = { "py2exe": {"compressed": 1,
                                   "optimize": 2,
                                   'dist_dir': 'dist95',
                                   'excludes': [ 'pyTTS', 'sapi' ] + exclude_win,
                                   }},
            windows = [dict(script = "Main.py",
                            dest_base = r"Descent")],
            )
kwxp = dict(options = { "py2exe": {"compressed": 1,
                               "optimize": 2,
                               'typelibs': [('{C866CA3A-32F7-11D2-9602-00C04F8EE628}', 0, 5, 0)],
                               'dist_dir': 'distXP',
							   'packages': ['encodings'], 
                               'excludes': ['pyFlite'] + exclude_win,
                               }},
            windows = [dict(script = "Main.py",
                            dest_base = r"Descent")],
            )

kw = { 'xp': kwxp,
       '95': kw95,
       }

for win in [ 'xp' ]:
  setup(name="Descent into Madness v1",
        version="1.0",
        author="Matt Clark and Eden Kung",
        url='http://www.cs.unc.edu/Research/assist',
        description='Descent into Madness: A role-playing audio game.',
        # The lib directory contains everything except the executables and the python dll.
        zipfile = r"lib\sharedlib.zip",
        # use our build_installer class as extended py2exe build command
        cmdclass = {"py2exe": build_installer},
        data_files = ([('',[sys.exec_prefix + '/msvcr71.dll'])]+
               #('',glob.glob('*.xrc')+['HarkConfig.pkl']) +
               [(dirpath, [ os.path.join(dirpath, name) for name in filenames ])
                for edir in ['sounds', 'images']
                for (dirpath, dirnames, filenames) in os.walk(edir)
                if len(filenames) > 0
                ]),
        **kw[win]
    )
