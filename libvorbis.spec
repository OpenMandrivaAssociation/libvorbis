# libvorbis is used by libsndfile, libsndfile is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%endif

%define major 0
%define libname %mklibname vorbis %{major}
%define devname %mklibname -d vorbis
%define lib32name %mklib32name vorbis %{major}
%define dev32name %mklib32name -d vorbis

%define encmaj 2
%define libenc %mklibname vorbisenc %{encmaj}
%define lib32enc %mklib32name vorbisenc %{encmaj}

%define filemaj 3
%define libfile %mklibname vorbisfile %{filemaj}
%define lib32file %mklib32name vorbisfile %{filemaj}

%ifnarch %riscv
%global optflags %{optflags} -O3
%endif

# (tpg) enable PGO build
%bcond_without pgo

Summary:	The Vorbis General Audio Compression Codec
Name:		libvorbis
Version:	1.3.7
Release:	3
Group:		System/Libraries
License:	BSD
Url:		http://www.xiph.org/
Source0:	http://downloads.xiph.org/releases/vorbis/%{name}-%{version}.tar.gz
BuildRequires:	pkgconfig(ogg)
%if %{with compat32}
BuildRequires:	devel(libogg)
%endif

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

%if %{with compat32}
%package -n %{lib32name}
Summary:	Main library for %{name} (32-bit)
Group:		System/Libraries

%description -n %{lib32name}
This package contains the library needed to run programs dynamically
linked with %{name}.

%package -n %{lib32enc}
Summary:	Encoder specialized library for %{name} (32-bit)
Group:		System/Libraries

%description -n %{lib32enc}
This package contains the library needed for some programs using the
encoder capability of %{name}.

%package -n %{lib32file}
Summary:	File operations specialized library for %{name} (32-bit)
Group:		System/Libraries

%description -n %{lib32file}
This package contains the library needed for some programs using the
file operations capability of %{name}.

%package -n %{dev32name}
Summary:	Headers for developing programs that will use %{name} (32-bit)
Group:		Development/C
Requires:	%{devname} = %{version}-%{release}
Requires:	%{lib32name} = %{version}-%{release}
Requires:	%{lib32enc} = %{version}-%{release}
Requires:	%{lib32file} = %{version}-%{release}

%description -n %{dev32name}
This package contains the headers that programmers will need to develop
applications which will use %{name}.
%endif

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
export CONFIGURE_TOP="$(pwd)"

%if %{with compat32}
mkdir build32
cd build32
%configure32
%make_build
cd ..
%endif

mkdir build
cd build
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
%if %{with compat32}
%make_install -C build32
%endif
%make_install -C build
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

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/libvorbis.so.%{major}*

%files -n %{lib32enc}
%{_prefix}/lib/libvorbisenc.so.%{encmaj}*

%files -n %{lib32file}
%{_prefix}/lib/libvorbisfile.so.%{filemaj}*

%files -n %{dev32name}
%{_prefix}/lib/*.so
%{_prefix}/lib/pkgconfig/*
%endif
