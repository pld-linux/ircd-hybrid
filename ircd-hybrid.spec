Summary:	Internet Relay Chat Server
Name:		ircd-hybrid
Version:	6.3.1
Release:	1
License:	GPL
Group:		Daemons
Source0:	%{name}-%{version}.tgz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-config.patch
URL:		http://www.ircd-hybrid.org/
Prereq:		rc-scripts
Prereq:		/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Conflicts:	ircd

%define		_sysconfdir	/etc/ircd
%define		_localstatedir	/var/lib/ircd

%description
Ircd is the server (daemon) program for the Internet Relay Chat
Program. This version supports IPv6, too.

%description -l pl
Ircd jest serwerem us³ugi IRC (Internet Relay Chat Program). Ta wersja
wspiera tak¿e protokó³ IPv6.

%prep
%setup -q
%patch -p1

%build

%configure2_13
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_var}/log/ircd
install -d $RPM_BUILD_ROOT%{_libdir}/ircd
install -d $RPM_BUILD_ROOT%{_sbindir}
install -d $RPM_BUILD_ROOT%{_mandir}/man8
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/rc.d/init.d,/etc/sysconfig}
install -d $RPM_BUILD_ROOT%{_localstatedir}
install -d $RPM_BUILD_ROOT%{_libdir}/ircd
install src/ircd $RPM_BUILD_ROOT%{_sbindir}/ircd
install doc/simple.conf	$RPM_BUILD_ROOT%{_sysconfdir}/ircd.conf
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ircd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ircd

cd tools
	for i in fixklines mkpasswd viconf mkconf untabify; do
		install $i $RPM_BUILD_ROOT%{_libdir}/ircd/$i
	done
cd ..

for i in doc/*; do
	if [ -f $i ]; then gzip -9nf $i; fi
done
install doc/ircd.8.gz $RPM_BUILD_ROOT%{_mandir}/man8/ircd.8.gz

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
