# TODO:
# - add modyfications for use system avalaible shared adns library.
#
Summary:	Internet Relay Chat Server
Summary(pl):	
Name:		ircd-hybrid
Version:	6.3.1
Release:	1
License:	GPL v1
Group:		Daemons
Source0:	http://prdownloads.sourceforge.net/ircd-hybrid/%{name}-%{version}.tgz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-config.patch
Patch1:		%{name}-ac25x.patch
Patch2:		%{name}-ac_fixes.patch
URL:		http://www.ircd-hybrid.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	zlib-devel
Prereq:		rc-scripts
Prereq:		/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Conflicts:	ircd

%define		_sysconfdir	/etc/ircd
%define		_localstatedir	/var/lib/ircd

%description
Ircd-hybrid is the server (daemon) program for the Internet Relay Chat
Program. This version supports IPv6, too.

%description -l pl
Ircd-hybrid jest serwerem us³ugi IRC (Internet Relay Chat Program). Ta wersja
wspiera tak¿e protokó³ IPv6.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
mv -f autoconf/configure.in .
cp -f /usr/share/automake/config.* autoconf
aclocal
autoconf
CFLAGS="%{rpmcflags} %{?debug:-DDEBUGMODE}"
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir}/ircd,%{_var}/log/ircd,%{_sysconfdir}} \
	$RPM_BUILD_ROOT{%{_libdir}/ircd,%{_sbindir},%{_mandir}/man8} \
	$RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{_localstatedir}}

install src/ircd $RPM_BUILD_ROOT%{_sbindir}/ircd
install doc/simple.conf	$RPM_BUILD_ROOT%{_sysconfdir}/ircd.conf
install doc/ircd.8 $RPM_BUILD_ROOT%{_mandir}/man8
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ircd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ircd

cd tools
	for i in fixklines mkpasswd viconf mkconf untabify; do
		install $i $RPM_BUILD_ROOT%{_libdir}/ircd/$i
	done
cd ..

gzip -9nf doc/{*.txt,example.*,README*,simple.conf,Tao-of-IRC.940110} \
	RELNOTES ChangeLog Hybrid-team opers.txt

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid ircd`" ]; then
	if [ "`getgid ircd`" != "75" ]; then
		echo "Warning: group ircd haven't gid=75. Correct this before installing ircd" 1>&2
		exit 1
	fi
else
	%{_sbindir}/groupadd -f -g 75 ircd 2> /dev/null
fi
if [ -n "`id -u ircd 2>/dev/null`" ]; then
	if [ "`id -u ircd`" != "75" ]; then
		echo "Warning: user ircd haven't uid=75. Correct this before installing ircd" 1>&2
		exit 1
	fi
else
	%{_sbindir}/useradd -g ircd -d /etc/%{name} -u 75 -s /bin/true ircd 2> /dev/null
fi

%post
/sbin/chkconfig --add ircd
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/ircd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/ircd start\" to start IRC daemon."
fi

%preun
# If package is being erased for the last time.
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/ircd ]; then
		/etc/rc.d/init.d/ircd stop 1>&2
	fi
	/sbin/chkconfig --del ircd
fi

%postun
# If package is being erased for the last time.
if [ "$1" = "0" ]; then
	%{_sbindir}/userdel ircd 2> /dev/null
	%{_sbindir}/groupdel ircd 2> /dev/null
fi

%files
%defattr(644,root,root,755)
%doc doc/*.gz
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_libdir}/ircd/
%attr(770,root,ircd) %dir %{_var}/log/ircd
%attr(770,root,ircd) %dir %{_localstatedir}
%attr(770,root,ircd) %dir %{_sysconfdir}
%attr(660,ircd,ircd) %config(noreplace) %{_sysconfdir}/ircd.conf
%{_mandir}/man*/*
%attr(754,root,root) /etc/rc.d/init.d/ircd
%attr(644,root,root) /etc/sysconfig/ircd
