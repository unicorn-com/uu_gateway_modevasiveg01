# add --with fail2ban option, i.e. disable fail2ban by default
%bcond_with fail2ban

# apxs script location
%{!?_httpd_apxs: %global _httpd_apxs %{_bindir}/apxs}

# Module Magic Number
%{!?_httpd_mmn: %global _httpd_mmn %(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo missing-httpd-devel)}

# Configuration directory
%{!?_httpd_confdir: %global _httpd_confdir %{_sysconfdir}/httpd/conf.d}
%{!?_httpd_modconfdir: %global _httpd_modconfdir %{_sysconfdir}/httpd/conf.modules.d}
%{!?_httpd_moddir: %global _httpd_moddir %{_libdir}/httpd/modules}
%if %{with fail2ban}
 %{!?_fail2ban_confdir: %global _fail2ban_confdir %{_sysconfdir}/fail2ban/filter.d}
%endif


%global httpd24 1
%global rundir /run

Name:		mod_evasive
Version:	3.0
Release:	0%{?dist}
Summary:	Realtime blacklist module for Apache 2
Group:		System Environment/Daemons
License:	GPL 2.0
URL:		  https://github.com/keklabs/mod_evasive
Source0:  mod_evasive.c
Source1:  evasive.conf
Source2:  fail2ban-apache-modevasive.conf
Source3:  README.md
Source4:  LICENSE
Source5:  CHANGELOG
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(id -nu)
BuildRequires:	httpd-devel >= 2.4, pkgconfig
%if %{with fail2ban}
BuildRequires:  fail2ban
%endif
Requires:	httpd-mmn = %{_httpd_mmn}

%description
mod_evasive is an evasive maneuvers module for Apache to provide evasive action 
in the event of an HTTP DoS or DDoS attack or brute force attack. 
It is also designed to be a detection tool, and can be easily configured to 
talk to ipchains, firewalls, routers, and etcetera.

%prep
cp -p %{SOURCE0} mod_evasive.c
cp -p %{SOURCE1} evasive.conf
cp -p %{SOURCE3} README.md
cp -p %{SOURCE4} LICENSE
cp -p %{SOURCE5} CHANGELOG
%if %{with fail2ban}
 cp -p %{SOURCE2} fail2ban-apache-modevasive.conf
%endif


%build
%{_httpd_apxs} -c -Wc,"%{optflags} -Wall -pedantic -std=c99" mod_evasive.c

%install
rm -rf $RPM_BUILD_ROOT
install -Dm 755 .libs/mod_evasive.so $RPM_BUILD_ROOT%{_httpd_moddir}/mod_evasive.so
install -Dp -m 0644 evasive.conf $RPM_BUILD_ROOT%{_httpd_modconfdir}/00-evasive.conf
%if %{with fail2ban}
 install -Dp -m 0644 fail2ban-apache-modevasive.conf $RPM_BUILD_ROOT%{_fail2ban_confdir}/fail2ban-apache-modevasive.conf
%endif


%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README.md LICENSE CHANGELOG
%config(noreplace) %{_httpd_modconfdir}/00-evasive.conf
%{_httpd_moddir}/*.so
%if %{with fail2ban}
 %config(noreplace) %{_fail2ban_confdir}/fail2ban-apache-modevasive.conf
%endif


%changelog
* Fri Jan 25 2019 KekLabs <keklabs@gmail.com> - 3.0-0
- Forked from https://github.com/apisnetworks/mod_evasive
- SilentMode - possibility to log DOS client without blocking
- IgnoreQueryString - new option to ignore query string in page-hit URI
- Logging to Apache error logs
- HTTP-429 Too many requests as default status
- Dependency on fail2ban is now optional, use rpmbuild -ba mod_evasive.spec --with fail2ban to build RPM with fail2ban support
- Move evasive.conf to /etc/httpd/conf.modules.d configuration directory
- added testing script for Apache-Jmeter 5.0
- added docker files for Alpine and CentOS linux

* Fri Dec 14 2018 Matt Saladna <matt@apisnetworks.com> - 2.1-1
- ISE on exec()

* Sun Dec 02 2018 Matt Saladna <matt@apisnetworks.com> - 2.1-0
- Merge custom HTTP status, per-virtualhost patch from jvdmr/mod_evasive
- Improve bot penetration tracking with global hash table per process instead of per server rec
- Shorten hash markers
- Invert whitelist class resolution D -> C -> B -> A
- Send no-cache header when blocked

* Sun Apr 08 2018 Matt Saladna <matt@apisnetworks.com> - 2.0-0
- Initial release
