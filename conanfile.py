from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conanos.build import config_scheme
import os, shutil

class X264Conan(ConanFile):
    name = "x264"
    version = "0.157.r2935"
    description = "x264 is a free software library and application for encoding video streams into the H.264/MPEG-4 AVC compression format"
    url = "https://github.com/conanos/x264"
    homepage = "https://www.videolan.org/developers/x264.html"
    license = "GPL-2.0"
    exports = ["COPYING","x264.pc.in"]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = { "shared": [True, False], "fPIC": [True, False] }
    default_options = { 'shared': True, 'fPIC': True }


    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        config_scheme(self)

    def source(self):
        #ftp://ftp.videolan.org/pub/videolan/x264/snapshots/x264-snapshot-20181108-2245-stable.tar.bz2
        url_ = "https://github.com/ShiftMediaProject/x264/archive/{version}.tar.gz"
        tools.get(url_.format(version=self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        #with tools.chdir(self.source_subfolder):
        #    #with tools.environment_append({'AS': 'yasm'}):
        #        _args = ["--prefix=%s/builddir"%(os.getcwd()), "--enable-pic", "--disable-lavf"]

        #        if self.options.shared:
        #            _args.extend(['--enable-shared'])
        #        else:
        #            _args.extend(['--enable-static'])
        #        autotools = AutoToolsBuildEnvironment(self)
        #        autotools.configure(args=_args)
        #        autotools.make(args=["-j4"])
        #        autotools.install()
        if self.settings.os == "Windows":
            with tools.chdir(os.path.join(self._source_subfolder,"SMP")):
                msbuild = MSBuild(self)
                build_type = str(self.settings.build_type) + ("DLL" if self.options.shared else "")
                msbuild.build("x264.sln",upgrade_project=True, build_type=build_type)

    def package(self):
        if self.settings.os == "Windows":
            platform = {'x86': 'x86','x86_64': 'x64'}
            rplatform = platform.get(str(self.settings.arch))
            self.copy("*", dst=os.path.join(self.package_folder,"include"), src=os.path.join(self.build_folder,"..", "msvc","include"))
            for i in ["lib","bin"]:
                self.copy("*", dst=os.path.join(self.package_folder,i), src=os.path.join(self.build_folder,"..","msvc",i,rplatform))
            self.copy("*", dst=os.path.join(self.package_folder,"licenses"), src=os.path.join(self.build_folder,"..", "msvc","licenses"))

            tools.mkdir(os.path.join(self.package_folder,"lib","pkgconfig"))
            shutil.copyfile(os.path.join(self.build_folder, "x264.pc.in"),
                            os.path.join(self.package_folder,"lib","pkgconfig", "x264.pc"))
            replacements = {
                "@prefix@"      : self.package_folder,
                "@version@"      : self.version
            }
            if self.options.shared:
                replacements.update({
                    "-lx264" : "-lx264d"
                })
            for s, r in replacements.items():
                tools.replace_in_file(os.path.join(self.package_folder,"lib","pkgconfig", "x264.pc"),s,r)
            
        #if tools.os_info.is_linux:
        #    with tools.chdir(self.source_subfolder):
        #        self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

