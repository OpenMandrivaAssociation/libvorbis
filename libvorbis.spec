%define name libvorbis
%define version 1.2.0
%define theirversion %version
%define lib_name_orig libvorbis
%define lib_major 0
%define libname %mklibname vorbis %{lib_major}
%define libnamedev %mklibname -d vorbis
%define lib_enc_major 2
%define lib_enc_name %mklibname vorbisenc %{lib_enc_major}
%define lib_file_major 3
%define lib_file_name %mklibname vorbisfile %{lib_file_major}
%define oggver 1.1

Name: %{name}
Summary: The Vorbis General Audio Compression Codec
Version: %{version}
Release: %mkrel 4
Group: System/Libraries
License: BSD
URL: http://www.xiph.org/
Source:	http://downloads.xiph.org/releases/vorbis/%{name}-%{theirversion}.tar.bz2
Patch0: libvorbis-1.0rc3-fix-optflags.patch
Patch1: libvorbis-1.0-lib64.patch
Patch2: libvorbis-r14598-CVE-2008-1420.patch
Patch3: libvorbis-r14602-CVE-2008-1419.patch
Patch4: libvorbis-r14602-CVE-2008-1423.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: libogg-devel >= %oggver
BuildRequires: glibc-static-devel
#gw: if patched
BuildRequires: automake1.7

%description
Ogg Vorbis is a fully open, non-proprietary, patent-and-royalty-free,
general-purpose compressed audio format for audio and music at fixed 
and variable bitrates from 16 to 128 kbps/channel.

Find some free Ogg Vorbis music here: http://www.vorbis.com/music.html

%package -n %{libname}
Summary: Main library for %{name}
Group: System/Libraries
Obsoletes: oggvorbis
Provides: oggvorbis = %{version}-%{release}
Provides: %{name} = %{version}-%{release}

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with %{name}.

%package -n %{libnamedev}
Summary: Headers for developing programs that will use %{name}
Group: Development/C
Requires: %{libname} = %{version}
Requires: %{lib_enc_name} = %{version}
Requires: %{lib_file_name} = %{version}
Requires: libogg-devel >= %{oggver}
Provides: %{lib_name_orig}-devel = %{version}-%{release}
Provides: %{name}%{lib_major}-devel = %{version}-%{release}
Obsoletes: oggvorbis-devel
Provides: oggvorbis-devel = %{version}-%{release}
Obsoletes: %mklibname -d vorbis 0

%description -n %{libnamedev}
This package contains the headers that programmers will need to develop
applications which will use %{name}.

%package -n %{lib_enc_name}
Summary: Encoder specialized library for %{name}
Group: System/Libraries

%description -n %{lib_enc_name}
This package contains the library needed for some programs using the
encoder capability of %{name}.

%package -n %{lib_file_name}
Summary: File operations specialized library for %{name}
Group: System/Libraries
Requires: %{libname} = %{version}

%description -n %{lib_file_name}
This package contains the library needed for some programs using the
file operations capability of %{name}.

%prep
%setup -q -n %{name}-%{theirversion}
%patch0 -p0
%patch1 -p1 -b .lib64
%patch2
%patch3
%patch4
# Regenerate aclocal.m4 to get the system ogg.m4.
# (aka don't use the package XIPH_PATH_OGG macro)
perl -ni -e "/^AC_DEFUN.XIPH_PATH_OGG/ .. /^\]\)$/ or print" acinclude.m4
aclocal-1.7
WANT_AUTOCONF_2_5=1 autoconf
automake-1.7 -a -c

%build
%configure2_5x
make

%install
rm -rf $RPM_BUILD_ROOT installed-docs
make DESTDIR=$RPM_BUILD_ROOT install
mv $RPM_BUILD_ROOT/%{_datadir}/doc installed-docs

%clean 
rm -rf $RPM_BUILD_ROOT

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%post -n %{lib_enc_name} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%post -n %{lib_file_name} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun -n %{lib_enc_name} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun -n %{lib_file_name} -p /sbin/ldconfig
%endif

%files -n %{libname}
%defattr(-,root,root)
%doc COPYING AUTHORS README
%{_libdir}/%{lib_name_orig}.so.%{lib_major}*

%files -n %{lib_enc_name}
%defattr(-,root,root)
%{_libdir}/%{lib_name_orig}enc.so.%{lib_enc_major}*

%files -n %{lib_file_name}
%defattr(-,root,root)
%{_libdir}/%{lib_name_orig}file.so.%{lib_file_major}*

%files -n %{libnamedev}
%defattr(-,root,root)
%doc installed-docs
%{_includedir}/vorbis
%{_libdir}/*.so
%{_libdir}/*.*a
%{_datadir}/aclocal/vorbis.m4
%{_libdir}/pkgconfig/*


