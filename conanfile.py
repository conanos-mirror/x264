from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from shutil import copyfile
import os

class X264Conan(ConanFile):
    name = "x264"
    version = "20181108-2245"
    description = "x264 is a free software library and application for encoding video streams into the H.264/MPEG-4 AVC compression format"
    url = "https://github.com/conan-multimedia/x264"
    homepage = "https://www.videolan.org/developers/x264.html"
    license = "GPL"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    source_subfolder = "source_subfolder"

    def source(self):
        #ftp://ftp.videolan.org/pub/videolan/x264/snapshots/x264-snapshot-20181108-2245-stable.tar.bz2
        tools.get('http://download.videolan.org/pub/x264/snapshots/{name}-snapshot-{version}-stable.tar.bz2'.format(name=self.name, version=self.version))
        extracted_dir = self.name + "-snapshot-" + self.version + "-stable"
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            #with tools.environment_append({'AS': 'yasm'}):
                _args = ["--prefix=%s/builddir"%(os.getcwd()), "--enable-pic", "--disable-lavf"]

                if self.options.shared:
                    _args.extend(['--enable-shared'])
                else:
                    _args.extend(['--enable-static'])
                autotools = AutoToolsBuildEnvironment(self)
                autotools.configure(args=_args)
                autotools.make(args=["-j4"])
                autotools.install()

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

