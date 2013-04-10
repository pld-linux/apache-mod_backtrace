%define		mod_name	backtrace
%define 	apxs		/usr/sbin/apxs
Summary:	Apache module: collects backtraces on crashes
Summary(pl.UTF-8):	Moduł Apache:	zbiera informacje o awariach
Name:		apache-mod_%{mod_name}
Version:	0.1
Release:	0.20040317.6
License:	Apache v2.0
Group:		Networking/Daemons/HTTP
Source0:	http://people.apache.org/~trawick/mod_backtrace.c
# Source0-md5:	cd5361da31b3c1401e29ccb6e5220f6b
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.0
BuildRequires:	rpmbuild(macros) >= 1.268
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
%setup -q -c -T
install %{SOURCE0} .

%build
%{apxs} -c mod_%{mod_name}.c -o mod_%{mod_name}.la

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir},/var/log/httpd}
install .libs/mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}

touch $RPM_BUILD_ROOT/var/log/httpd/backtrace_log

cat > $RPM_BUILD_ROOT%{_sysconfdir}/90_mod_%{mod_name}.conf << 'EOF'
LoadModule %{mod_name}_module modules/mod_%{mod_name}.so
EnableExceptionHook On
BacktraceLog /var/log/httpd/backtrace_log
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f /var/log/httpd/backtrace_log ]; then
	:> /var/log/httpd/backtrace_log
	chown root:http /var/log/httpd/backtrace_log
	chmod 620 /var/log/httpd/backtrace_log
fi
%service -q httpd restart

%postun
if [ "$1" = "0" ]; then
	%service -q httpd restart
fi

%files
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/*.so
# open for append by webserver
%attr(620,root,http) %ghost /var/log/httpd/backtrace_log
