%define major 0
%define libname %mklibname vorbis %{major}
%define devname %mklibname -d vorbis

%define encmaj 2
%define libenc %mklibname vorbisenc %{encmaj}

%define filemaj 3
%define libfile %mklibname vorbisfile %{filemaj}

%ifnarch %riscv
%global optflags %{optflags} -O3 -Qunused-arguments
%endif

# (tpg) enable PGO build
%bcond_without pgo

Summary:	The Vorbis General Audio Compression Codec
Name:		libvorbis
Version:	1.3.6
Release:	5
Group:		System/Libraries
License:	BSD
Url:		http://www.xiph.org/
Source0:	http://downloads.xiph.org/releases/vorbis/%{name}-%{version}.tar.gz
BuildRequires:	pkgconfig(ogg)

%description
Ogg Vorbis is a fully open, non-proprietary, patent-and-royalty-free,
general-purpose compressed audio format for audio and music at fixed
and variable bitrates from 16 to 128 kbps/channel.

Find some free Ogg Vorbis music here: http://www.vorbis.com/music.html

%package -n %{libname}
Summary:	Main library for %{name}
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with %{name}.

%package -n %{libenc}
Summary:	Encoder specialized library for %{name}
Group:		System/Libraries

%description -n %{libenc}
This package contains the library needed for some programs using the
encoder capability of %{name}.

%package -n %{libfile}
Summary:	File operations specialized library for %{name}
Group:		System/Libraries

%description -n %{libfile}
This package contains the library needed for some programs using the
file operations capability of %{name}.

%package -n %{devname}
Summary:	Headers for developing programs that will use %{name}
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Requires:	%{libenc} = %{version}-%{release}
Requires:	%{libfile} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
This package contains the headers that programmers will need to develop
applications which will use %{name}.

%prep
%autosetup -p1

#fix build with new automake
sed -i -e 's,AM_CONFIG_HEADER,AC_CONFIG_HEADERS,g' configure.*
# drop weird flags
sed -i 's/-O20/$CFLAGS/' configure.ac
sed -i 's!-mno-ieee-fp!!g' configure.ac
libtoolize --install --copy --force --automake
aclocal -I m4
autoconf -I m4
autoheader -I m4
automake --add-missing --copy --foreign

%build
%if %{with pgo}
export LLVM_PROFILE_FILE=%{name}-%p.profile.d
export LD_LIBRARY_PATH="$(pwd)"
CFLAGS="%{optflags} -fprofile-instr-generate" \
CXXFLAGS="%{optflags} -fprofile-instr-generate" \
FFLAGS="$CFLAGS_PGO" \
FCFLAGS="$CFLAGS_PGO" \
LDFLAGS="%{ldflags} -fprofile-instr-generate" \
%configure --disable-static
%make_build

make LIBS=-lm check -j1
unset LD_LIBRARY_PATH
unset LLVM_PROFILE_FILE
llvm-profdata merge --output=%{name}.profile *.profile.d

make clean

CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
%endif
%configure --disable-static
%make_build

%install
%make_install
mv %{buildroot}/%{_datadir}/doc installed-docs

%files -n %{libname}
%doc AUTHORS
%{_libdir}/libvorbis.so.%{major}*

%files -n %{libenc}
%{_libdir}/libvorbisenc.so.%{encmaj}*

%files -n %{libfile}
%{_libdir}/libvorbisfile.so.%{filemaj}*

%files -n %{devname}
%doc installed-docs
%{_includedir}/vorbis
%{_libdir}/*.so
%{_datadir}/aclocal/vorbis.m4
%{_libdir}/pkgconfig/*

