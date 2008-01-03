Summary:	Binc IMAP server
Name:		bincimap
Version:	1.2.13
Release:	%mkrel 2
License:	GPL
Group:		System/Servers
URL:		http://www.bincimap.org/
Source0:	http://www.bincimap.org/dl/tarballs/1.2/%{name}-%{version}final.tar.bz2
Source1:	bincimap.cnf.bz2
Source2:	mkimapdcert.bz2
# http://src.andreas.hanssen.name/multichkpwds/trunk/multichkpwds.c
Source3:	multichkpwds-2.0.tar.bz2
Patch0:		bincimap-1.2.0-misc_fixes_to_finally_make_it_work_out_of_the_box.patch
Patch1:		multichkpwds-2.0-compile_fixer.diff
BuildRequires:	autoconf2.5
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libgcc1
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
BuildRequires:	openssl-devel
BuildRequires:	zlib-devel
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(post): checkpassword-pam
Requires(preun): checkpassword-pam
Requires(post): xinetd
Requires(preun): xinetd
Requires:	checkpassword-pam
Requires:	xinetd
Requires:	openssl
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Binc IMAP is an IMAP server, written in C++ for the Linux platform. It
supports Dan J. Bernstein's Maildir format and checkpassword
authentication.

As an alternative to existing similar IMAP servers, Binc IMAP strives
to be:

* very easy to install and use, but robust, stable and secure
* absolutely compliant with the IMAP4rev1 protocol
* simple and modular in design, making it very easy for
  third parties to utilize the source code and enhance the
  product.

%prep

%setup -q -n %{name}-%{version}final -a3
%patch0 -p1 -b .misc_fixes_to_finally_make_it_work_out_of_the_box
%patch1 -p0 -b .compile_fixer

%build

%configure2_5x \
    --prefix=%{_prefix} \
    --exec-prefix=%{_sbindir} \
    --bindir=%{_sbindir} \
    --sbindir=%{_sbindir} \
    --sysconfdir=%{_sysconfdir} \
    --localstatedir=%{_localstatedir}/bincimap-chroot

%make

# make multichkpwds
gcc %{optflags} -o multichkpwds multichkpwds-*/multichkpwds.c

%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/ssl/bincimap
install -d %{buildroot}%{_sysconfdir}/xinetd.d
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_mandir}/man{1,5}
install -d %{buildroot}%{_localstatedir}/bincimap-chroot

install -m755 src/bincimapd %{buildroot}%{_sbindir}/
install -m755 src/bincimap-up %{buildroot}%{_sbindir}/
install -m755 multichkpwds %{buildroot}%{_bindir}/

install -m644 conf/bincimap.conf %{buildroot}%{_sysconfdir}/bincimap.conf
install -m644 conf/xinetd-bincimap %{buildroot}%{_sysconfdir}/xinetd.d/bincimap
install -m644 conf/xinetd-bincimaps %{buildroot}%{_sysconfdir}/xinetd.d/bincimaps

install -m644 man/bincimapd.1 %{buildroot}%{_mandir}/man1/
install -m644 man/bincimap-up.1 %{buildroot}%{_mandir}/man1/
install -m644 man/bincimap.conf.5 %{buildroot}%{_mandir}/man5/

bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/ssl/bincimap/bincimap.cnf
bzcat %{SOURCE2} > mkimapdcert

chmod 644 %{buildroot}%{_sysconfdir}/ssl/bincimap/bincimap.cnf

# fix the DJB scripts directory
find service -type f -name "Makefile*" | xargs rm -f
find service -type f -name "down" | xargs rm -f
find service -type f -name "*.in" | xargs rm -f

%pre
%_pre_useradd bincimap %{_localstatedir}/bincimap-chroot /bin/false

%post
if [ $1 = "1" ]; then 
  #Create a self-signed server key and certificate 
  #The script checks first if they exists, if yes, it exits, 
  #otherwise, it creates them.
  if ! [ -f %{_sysconfdir}/ssl/bincimap/bincimap.pem ];then
    sh %{_docdir}/%{name}-%{version}/mkimapdcert >/dev/null 
  fi
fi
service xinetd condrestart

%postun
%_postun_userdel bincimap
service xinetd condrestart

%clean
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

%files
%defattr(-, root, root)
%doc service mkimapdcert AUTHORS ChangeLog README TODO doc/bincimap* doc/*.txt
%doc multichkpwds-*/multichkpwds.README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/bincimap.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/xinetd.d/bincimap
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/xinetd.d/bincimaps
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ssl/bincimap/bincimap.cnf
%attr(0755,root,root) %{_bindir}/multichkpwds
%attr(0755,root,root) %{_sbindir}/bincimap-up
%attr(0755,root,root) %{_sbindir}/bincimapd
%attr(0644,root,root) %{_mandir}/man1/bincimapd.1*
%attr(0644,root,root) %{_mandir}/man1/bincimap-up.1*
%attr(0644,root,root) %{_mandir}/man5/bincimap.conf.5*
%dir %attr(0755,bincimap,bincimap) %{_localstatedir}/bincimap-chroot


