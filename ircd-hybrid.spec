# TODO:
# - add modyfications for use system avalaible shared adns library.
# - rewrite ipv6 support to work with non-v6 systems
# - check alpha patch, it compiles but doesnt work ;/
#
# Conditional build:
# _with_ipv6		- enable ipv6 support - do not use for v4-only machines.
# _with_longnicks	- enable long nicknames.  All servers on the network
# 					  must use the same length.
# _with_longtopics	- enable long topics.  All servers on the network
# 					  must use the same length.
#
Summary:	Internet Relay Chat Server
Summary(pl):	Serwer IRC
Name:		ircd-hybrid
Version:	7.0
Release:	3.2
Epoch:		1
License:	GPL v2
Group:		Daemons
Source0:	http://dl.sourceforge.net/%{name}/%{name}-%{version}.tgz
# Source0-md5:	bee69c994c70fb29a711614150587cd4
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
Patch0:		%{name}-config.patch
Patch1:		%{name}-change_uid.patch
Patch2:		%{name}-opt.patch
URL:		http://www.ircd-hybrid.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	zlib-devel
Prereq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	ircd
Obsoletes:	ircd6

%define		_sysconfdir	/etc/ircd
%define		_localstatedir	/var/lib/ircd

%description
Ircd-hybrid is an advanced IRC server which is most commonly used on
the EFNet IRC network. It is fast, reliable, and powerful. This
version supports IPv6.

%description -l pl
Ircd-hybrid jest zaawansowanym serwerem IRC, najczê¶ciej u¿ywanym w
sieci EFNet. Jest szybki, stabilny i wydajny. Ta wersja obs³uguje
IPv6.

%prep
%setup -q
%patch0 -p1
%patch1	-p1
%patch2 -p1

%build
mv -f autoconf/{configure.in,acconfig.h} .
cp -f %{_datadir}/automake/config.* autoconf
%{__aclocal}
%{__autoconf}
CFLAGS="%{rpmcflags} %{?debug:-DDEBUGMODE}"
%configure \
		--enable-zlib \
		%{?_with_ipv6:--enable-ipv6} \
		--enable-small-net \
		%{?_with_longnicks:--with-nicklen=20} \
		%{?_with_longtopics:--with-topiclen=500} \
		%{?_with_ssl:--enable-openssl} \
		%{!?_with_ssl:--disable-openssl} \
		--enable-shared-modules \
		--with-maxclients=512
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir}/ircd,%{_var}/log/ircd,%{_sysconfdir}} \
	$RPM_BUILD_ROOT{%{_libdir}/ircd/{modules{,/autoload},tools,help},%{_sbindir},%{_mandir}/man8} \
	$RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{_localstatedir},/var/run/ircd}

install src/ircd $RPM_BUILD_ROOT%{_sbindir}/ircd
install servlink/servlink $RPM_BUILD_ROOT%{_sbindir}/servlink
install doc/ircd.8 $RPM_BUILD_ROOT%{_mandir}/man8
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ircd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ircd
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/ircd.conf

cd modules
	install *.so $RPM_BUILD_ROOT%{_libdir}/ircd/modules/autoload
	cd core
		install *.so $RPM_BUILD_ROOT%{_libdir}/ircd/modules
	cd ..
cd ..

cd tools
	for i in convertconf convertilines convertklines encspeed mkkeypair mkpasswd untabify viconf; do
		install $i $RPM_BUILD_ROOT%{_libdir}/ircd/tools/$i
	done
cd ..

cd help
	cp -rf opers users $RPM_BUILD_ROOT%{_libdir}/ircd/help
cd ..

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid ircd`" ]; then
       if [ "`getgid ircd`" != "75" ]; then
               echo "Error: group ircd doesn't have gid=75. Correct this before installing ircd." 1>&2
               exit 1
       fi
else
       /usr/sbin/groupadd -f -g 75 ircd 2> /dev/null
fi
if [ -n "`id -u ircd 2>/dev/null`" ]; then
       if [ "`id -u ircd`" != "75" ]; then
               echo "Error: user ircd doesn't have uid=75. Correct this before installing ircd." 1>&2
               exit 1
       fi
else
       /usr/sbin/useradd -g ircd -d /etc/ircd -u 75 -c "IRC service account" -s /bin/true ircd 2> /dev/null
fi

%post
/sbin/chkconfig --add ircd
if [ -f /var/lock/subsys/ircd ]; then
	/etc/rc.d/init.d/ircd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/ircd start\" to start IRC daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/ircd ]; then
		/etc/rc.d/init.d/ircd stop 1>&2
	fi
	/sbin/chkconfig --del ircd
fi

%postun
if [ "$1" = "0" ]; then
       /usr/sbin/userdel ircd 2> /dev/null
       /usr/sbin/groupdel ircd 2> /dev/null
fi

%files
%defattr(644,root,root,755)
%doc doc/{*.txt,*.conf,server-version-info,technical} RELNOTES ChangeLog Hybrid-team BUGS TODO
%attr(755,root,root) %{_sbindir}/*
%attr(770,root,ircd) %dir %{_sysconfdir}
%attr(660,ircd,ircd) %config(noreplace) %{_sysconfdir}/ircd.conf
%attr(754,root,root) /etc/rc.d/init.d/ircd
%attr(644,root,root) /etc/sysconfig/ircd
%dir %{_libdir}/ircd
%dir %{_libdir}/ircd/modules
%dir %{_libdir}/ircd/tools
%dir %{_libdir}/ircd/help
%attr(755,root,root) %{_libdir}/ircd/modules/*
%attr(755,root,root) %{_libdir}/ircd/tools/*
%{_libdir}/ircd/help/*
%attr(770,root,ircd) %dir %{_var}/log/ircd
%attr(770,root,ircd) %dir %{_localstatedir}
%{_mandir}/man*/*
%attr(770,ircd,ircd) %dir /var/run/ircd
