import json, os
from conans import ConanFile, VisualStudioBuildEnvironment, MSBuild, tools


class QtavConan(ConanFile):
    name = "QtAV"
    version = "1.12.0"
    license = "LGPLv2.1"
    url = "https://github.com/Tereius/conan-QtAV.git"
    description = "QtAV is a multimedia playback library based on Qt and FFmpeg"
    author = "Björn Stresing"
    homepage = "https://www.qtav.org/"
    requires = "Qt/[>=5.0]@bincrafters/stable", "ffmpeg/[>=3.4]@bincrafters/stable"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = ("shared=True",
                        "Qt:shared=True",
                        "Qt:GUI=True",
                        "Qt:widgets=True",
                        "Qt:openssl=yes",
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
                        "ffmpeg:openjpeg=False",
                        "ffmpeg:openh264=False",
                        "ffmpeg:opus=False",
                        "ffmpeg:vorbis=False",
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
        git.checkout("7f6929b49c25ca475a08f87e8b52aa1642d109dd")

    def build(self):
        env_build = VisualStudioBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            vcvars = tools.vcvars_command(self.settings)
            self.run('%s && qmake -r -tp vc "LIBS+=%s" "INCLUDEPATH+=%s" QtAV.pro' % (vcvars, ' -L'+ ' -L'.join(env_build.lib_paths), ' '.join(env_build.include_paths)), cwd="QtAV")
            ms_env = MSBuild(self)
            ms_env.build(project_file="QtAV/QtAV.sln")

    #def package(self):

    def package_info(self):
        self.cpp_info.includedirs = ['include']  # Ordered list of include paths
        self.cpp_info.libs = []  # The libs to link against
        self.cpp_info.libdirs = ['lib']  # Directories where libraries can be found
        self.cpp_info.builddirs = ['cmake']  # Ordered list with build scripts paths, by default [‘’]. CMake will search in these dirs for cmake files, like findXXX.cmake
        self.cpp_info.bindirs = ['bin']  # Directories where executables and shared libs can be found
        self.cpp_info.defines = []  # preprocessor definitions
        self.cpp_info.cflags = []  # pure C flags
        self.cpp_info.cppflags = []  # C++ compilation flags
        self.cpp_info.sharedlinkflags = []  # linker flags
        self.cpp_info.exelinkflags = []  # linker flags
