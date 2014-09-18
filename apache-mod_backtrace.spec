%define		mod_name	backtrace
%define 	apxs		/usr/sbin/apxs
Summary:	Apache module: collects backtraces on crashes
Summary(pl.UTF-8):	Moduł Apache:	zbiera informacje o awariach
Name:		apache-mod_%{mod_name}
Version:	2.01
Release:	1
License:	Apache v2.0
Group:		Networking/Daemons/HTTP
Source0:	http://emptyhammock.com/downloads/wku_bt-%{version}.zip
# Source0-md5:	32bbe148f6cb2b8714166388f94d9129
URL:		http://emptyhammock.com/projects/httpd/diag/
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.0
BuildRequires:	libunwind-devel
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	apache-mod_whatkilledus >= %{version}
Requires:	apache(modules-api) = %apache_modules_api
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)/conf.d
%define		_pkglogdir	%(%{apxs} -q PREFIX 2>/dev/null)/logs

%description
mod_backtrace is an experimental module for Apache httpd 2.x which
collects backtraces when a child process crashes.

%description -l pl.UTF-8
mod_backtrace jest eksperymentalnym modułem dla apache'a 2.x, który
rejestruje informacje o błędach w sytuacji kiedy proces potomny
serwera apache ulegnie zniszczeniu.

%prep
%setup -q -n wku_bt-%{version}

%build
%{apxs} -c mod_%{mod_name}.c diag.c \
	-DDIAG_HAVE_LIBUNWIND_BACKTRACE=1 \
%if "%{__lib}" == "lib64"
	-DDIAG_BITS_64=1 \
%endif
	-lunwind \
	-o mod_%{mod_name}.la

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}}
install .libs/mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}


cat > $RPM_BUILD_ROOT%{_sysconfdir}/90_mod_%{mod_name}.conf << 'EOF'
LoadModule %{mod_name}_module modules/mod_%{mod_name}.so
#BacktraceErrorLogging Off
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%service -q httpd restart

%postun
if [ "$1" = "0" ]; then
	%service -q httpd restart
fi

%triggerpostun -- %{name} < 2.00
sed -i -e 's#^EnableExceptionHook.*##g' -e 's#BacktraceLog.*##g' %{_sysconfdir}/90_mod_%{mod_name}.conf

%files
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/*.so
