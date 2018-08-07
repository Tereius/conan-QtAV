import os
from shutil import copyfile
from conans import ConanFile, VisualStudioBuildEnvironment, MSBuild, tools


class QtavConan(ConanFile):
    name = "QtAV"
    version = "1.13.0-SNAPSHOT"
    license = "LGPLv2.1"
    url = "https://github.com/Tereius/conan-QtAV.git"
    description = "QtAV is a multimedia playback library based on Qt and FFmpeg"
    author = "Bjoern Stresing"
    homepage = "https://www.qtav.org/"
    requires = "Qt/5.11.1@bincrafters/stable", "ffmpeg/4.0@bincrafters/stable"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = ("shared=True",
                        "Qt:shared=True",
                        "Qt:GUI=True",
                        "Qt:widgets=True",
                        "Qt:openssl=True",
                        "Qt:qtbase=True",
                        "Qt:qtsvg=True",
                        "Qt:qtdeclarative=True",
                        "Qt:qttools=True",
                        "Qt:qttranslations=True",
                        "Qt:qtrepotools=True",
                        "Qt:qtqa=True",
                        "Qt:qtgraphicaleffects=True",
                        "Qt:qtquickcontrols=True",
                        "Qt:qtquickcontrols2=True",
                        "ffmpeg:shared=True",
                        "ffmpeg:lzma=False",
                        "ffmpeg:bzlib=False",
                        "ffmpeg:iconv=False",
                        "ffmpeg:freetype=False",
                        "ffmpeg:openjpeg=False",
                        "ffmpeg:openh264=False",
                        "ffmpeg:opus=False",
                        "ffmpeg:vorbis=False",
                        "ffmpeg:zmq=False",
                        "ffmpeg:sdl2=False",
                        "ffmpeg:x264=False",
                        "ffmpeg:x265=False",
                        "ffmpeg:vpx=False",
                        "ffmpeg:mp3lame=False",
                        "ffmpeg:fdk_aac=False")
    #generators = "cmake"
    build_policy = "missing"

    def source(self):
        git = tools.Git(folder="QtAV")
        git.clone("https://github.com/wang-bin/QtAV.git")
        git.checkout("34afa14316c2052bcef2822e82b32c11e0939e54")

    def build(self):
        env_build = VisualStudioBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            vcvars = tools.vcvars_command(self.settings)
            self.run('%s && qmake -r -tp vc "LIBS+=%s" "INCLUDEPATH+=%s" QtAV.pro' % (vcvars, ' -L'+ ' -L'.join(env_build.lib_paths), ' '.join(env_build.include_paths)), cwd="QtAV")
            ms_env = MSBuild(self)
            ms_env.build(project_file="QtAV/QtAV.sln", targets=["QtAV", "QtAVWidgets"], upgrade_project=False) # Missing dependency information between targets
            ms_env.build(project_file="QtAV/QtAV.sln", upgrade_project=False)

    def package(self):

        arch = str(self.settings.arch)
        self.copy("QtAV/lib_win_" + arch + "/*Qt*AV*.lib", dst="lib", keep_path=False)
        #self.copy("QtAV/lib_win_" + arch + "/QtAV1.lib", dst="lib/Qt5AV.lib", keep_path=False)
        #self.copy("QtAV/lib_win_" + arch + "/QtAVd1.lib", dst="lib/Qt5AVd.lib", keep_path=False)
        self.copy("QtAV/lib_win_" + arch + "/*QmlAV*.lib", dst="lib/qml/QtAV", keep_path=False)
        #self.copy("QtAV/lib_win_" + arch + "/QtAVWidgets1.lib", dst="lib/Qt5AVWidgets.lib", keep_path=False)
        #self.copy("QtAV/lib_win_" + arch + "/QtAVWidgetsd1.lib", dst="lib/Qt5AVWidgetsd.lib", keep_path=False)
        self.copy("QtAV/bin/Qt*AV*.dll", dst="bin", keep_path=False)
        self.copy("QtAV/bin/*QmlAV*.dll", dst="lib/qml/QtAV", keep_path=False)
        self.copy("QtAV/src/QtAV/*.h", dst="include/QtAV", keep_path=False)
        copyfile(self.build_folder + "/QtAV/src/QtAV/QtAV", self.package_folder + "/include/QtAV/QtAV") # Not a folder
        self.copy("QtAV/widgets/QtAVWidgets/*.h", dst="include/QtAVWidgets", keep_path=False)
        copyfile(self.build_folder + "/QtAV/widgets/QtAVWidgets/QtAVWidgets", self.package_folder + "/include/QtAVWidgets/QtAVWidgets") # Not a folder
        copyfile(self.build_folder + "/QtAV/qml/qmldir", self.package_folder + "/lib/qml/QtAV/qmldir") # Not a folder
        self.copy("QtAV/qml/Video.qml", dst="lib/qml/QtAV", keep_path=False)
        self.copy("QtAV/qml/plugins.qmltypes", dst="lib/qml/QtAV", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.cpp_info.libs = []
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.builddirs = ['cmake']
        self.cpp_info.bindirs = ['bin']
        self.cpp_info.defines = []
        self.cpp_info.cflags = []
        self.cpp_info.cppflags = []
        self.cpp_info.sharedlinkflags = []
        self.cpp_info.exelinkflags = []
