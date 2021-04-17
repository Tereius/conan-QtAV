#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from shutil import copyfile
from conans import ConanFile, VisualStudioBuildEnvironment, AutoToolsBuildEnvironment, MSBuild, tools


class QtavConan(ConanFile):
    name = "QtAV"
    version = "1.13.0-SNAPSHOT"
    license = "LGPLv2.1"
    url = "https://github.com/Tereius/conan-QtAV.git"
    description = "QtAV is a multimedia playback library based on Qt and FFmpeg"
    author = "Bjoern Stresing"
    homepage = "https://www.qtav.org/"
    requires = "Qt/[^5.12]@tereius/stable", "ffmpeg/[^4.0]@tereius/stable"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = ("shared=True",
                        "Qt:shared=True",
                        "Qt:GUI=True",
                        "Qt:widgets=True",
                        "Qt:openssl=False",
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
                        "ffmpeg:shared=True")

    def source(self):
        git = tools.Git(folder="QtAV")
        git.clone("https://github.com/wang-bin/QtAV.git")
        git.checkout("34afa14316c2052bcef2822e82b32c11e0939e54")
        self.run("git submodule init && git submodule update", cwd="QtAV")
        tools.replace_in_file(os.path.join(self.source_folder, "QtAV", "qml", "SGVideoNode.cpp"), "#include <QtQuick/QSGMaterialShader>", "#include <QtQuick/QSGMaterialShader>\n#include <QtQuick/QSGMaterial>")
        tools.replace_in_file(os.path.join(self.source_folder, "QtAV", "src", "QtAV", "FilterContext.h"), "#include <QtGui/QPainter>", "#include <QtGui/QPainter>\n#include <QtGui/QPainterPath>")

    def configure(self):
        if self.settings.os == 'Android':
            self.options["Qt"].qtandroidextras = True

    def build(self):

        build_type = "debug" if self.settings.build_type == "Debug" else "release"

        if self.settings.os == "Windows":
            env_build = VisualStudioBuildEnvironment(self)
            with tools.environment_append(env_build.vars):
                vcvars = tools.vcvars_command(self.settings)
                tools.replace_in_file("QtAV/.qmake.conf", "QTAV_MAJOR_VERSION = 1", "QTAV_MAJOR_VERSION = 1\nLIBS += %s\nINCLUDEPATH += %s\nCONFIG += %s\n" % (' -L'+ ' -L'.join(env_build.lib_paths), ' '.join(env_build.include_paths), build_type))
                self.run('%s && qmake -r -tp vc QtAV.pro' % (vcvars), cwd="QtAV")
                ms_env = MSBuild(self)
                ms_env.build(project_file="QtAV/QtAV.sln", targets=["QtAV", "QtAVWidgets"], upgrade_project=False) # Missing dependency information between targets
                ms_env.build(project_file="QtAV/QtAV.sln", upgrade_project=False)
        else:
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            envvars = autotools.vars
            envvars["LD_LIBRARY_PATH"] = "".join([i+":" for i in autotools.library_paths])
            envvars["LD_RUN_PATH"] = "".join([i+":" for i in autotools.library_paths])
            with tools.environment_append(envvars):
                if "RASPBIAN_ROOTFS" in os.environ:
                    tools.replace_in_file("QtAV/.qmake.conf", "QTAV_MAJOR_VERSION = 1", "QTAV_MAJOR_VERSION = 1\nDEFINES += CAPI_LINK_EGL\n")
                tools.replace_in_file("QtAV/.qmake.conf", "QTAV_MAJOR_VERSION = 1", "CONFIG += no-examples\nQTAV_MAJOR_VERSION = 1\nLIBS += %s\nINCLUDEPATH += %s\nCONFIG += %s\n" % (' -L'+ ' -L'.join(autotools.library_paths), ' '.join(autotools.include_paths), build_type))
                self.run('qmake QtAV.pro', win_bash=tools.os_info.is_windows, cwd="QtAV")
                self.run("make -j %s" % tools.cpu_count(), win_bash=tools.os_info.is_windows, cwd="QtAV")
            

    def package(self):

        arch = "*"
        if self.settings.os == "Windows":
            self.copy("QtAV/lib_win_" + arch + "/*Qt*AV*.lib", dst="lib", keep_path=False)
        elif self.settings.os == "Android":
            self.copy("QtAV/lib_android_" + "/*Qt*AV*.so", dst="lib", keep_path=False)
        else:
            self.copy("QtAV/lib_linux_" + arch + "/*Qt*AV*.so*", dst="lib", keep_path=False, symlinks=True)
        

        #self.copy("QtAV/lib_win_" + arch + "/QtAV1.lib", dst="lib/Qt5AV.lib", keep_path=False)
        #self.copy("QtAV/lib_win_" + arch + "/QtAVd1.lib", dst="lib/Qt5AVd.lib", keep_path=False)

        if self.settings.os == "Windows":
            self.copy("QtAV/lib_win_" + arch + "/*QmlAV*.lib", dst="lib/qml/QtAV", keep_path=False)
        elif self.settings.os == "Android":
            self.copy("QtAV/lib_android_" + "/*QmlAV*.so", dst="lib/qml/QtAV", keep_path=False)
        else:
            self.copy("QtAV/lib_linux_" + arch + "/*QmlAV*.so", dst="lib/qml/QtAV", keep_path=False, symlinks=True)

        #self.copy("QtAV/lib_win_" + arch + "/QtAVWidgets1.lib", dst="lib/Qt5AVWidgets.lib", keep_path=False)
        #self.copy("QtAV/lib_win_" + arch + "/QtAVWidgetsd1.lib", dst="lib/Qt5AVWidgetsd.lib", keep_path=False)

        if self.settings.os == "Windows":
            self.copy("QtAV/bin/Qt*AV*.dll", dst="bin", keep_path=False)
            self.copy("QtAV/bin/*QmlAV*.dll", dst="lib/qml/QtAV", keep_path=False)

        self.copy("QtAV/src/QtAV/*.h", dst="include/QtAV", keep_path=False)
        copyfile(self.build_folder + "/QtAV/src/QtAV/QtAV", self.package_folder + "/include/QtAV/QtAV") # Not a folder
        self.copy("QtAV/widgets/QtAVWidgets/*.h", dst="include/QtAVWidgets", keep_path=False)
        copyfile(self.build_folder + "/QtAV/widgets/QtAVWidgets/QtAVWidgets", self.package_folder + "/include/QtAVWidgets/QtAVWidgets") # Not a folder
        self.copy("QtAV/qml/Video.qml", dst="lib/qml/QtAV", keep_path=False)
        self.copy("QtAV/qml/plugins.qmltypes", dst="lib/qml/QtAV", keep_path=False)
        copyfile(self.build_folder + "/QtAV/qml/qmldir", self.package_folder + "/lib/qml/QtAV/qmldir") # Not a folder

    def package_info(self):
        self.env_info.QML2_IMPORT_PATH.append(os.path.join(self.package_folder, "lib/qml/QtAV"))
