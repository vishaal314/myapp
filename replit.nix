{pkgs}: {
  deps = [
    pkgs.mariadb
    pkgs.poppler_utils
    pkgs.enscript
    pkgs.unzip
    pkgs.redis
    pkgs.libstdcxx5
    pkgs.glibc
    pkgs.gcc
    pkgs.glibcLocales
    pkgs.tk
    pkgs.tcl
    pkgs.qhull
    pkgs.pkg-config
    pkgs.gtk3
    pkgs.gobject-introspection
    pkgs.ghostscript
    pkgs.freetype
    pkgs.ffmpeg-full
    pkgs.cairo
  ];
}
