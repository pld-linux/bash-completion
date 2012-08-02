# vim:ft=spec
# TODO
# - finish v1.3 => v2 transition:
#   - deal with new completions
#   - revise enabling method (files are now per-command, not per-package)
# - bittorrent complete doesn't actually handle our prognames
# - use mkinitrd and update for geninitrd
# - can we have duplicate trigger on pwdutils pkg? merge files?
# - fix vim not to mark this file as bash
Summary:	bash-completion offers programmable completion for bash
Summary(pl.UTF-8):	Programowalne uzupełnianie nazw dla basha
Name:		bash-completion
Version:	2.0
Release:	0.1
Epoch:		1
License:	GPL v2+
Group:		Applications/Shells
Source0:	http://bash-completion.alioth.debian.org/files/%{name}-%{version}.tar.bz2
# Source0-md5:	0d903f398be8c8f24bc5ffa6f86127f8
Source1:	%{name}-poldek.sh
Source2:	%{name}.sh
# https://bugs.launchpad.net/ubuntu/+source/mysql-dfsg-5.0/+bug/106975
Source3:	http://launchpadlibrarian.net/19164189/mysqldump
# Source3-md5:	09e4885be92e032400ed702f39925d85
Source4:	http://svn.php.net/viewvc/pear2/sandbox/PEAR_BashCompletion/trunk/pear?revision=285425&view=co#/pear
# Source4-md5:	8ce77e4459e2c45e2096da8d03c8f43d
# https://alioth.debian.org/tracker/?func=detail&atid=413095&aid=312910&group_id=100114
Source5:	phing.sh
Patch0:		%{name}-rpm-cache.patch
Patch1:		pear.patch
URL:		http://bash-completion.alioth.debian.org/
BuildRequires:	sed >= 4.0
Requires(triggerpostun):	sed >= 4.0
Requires:	bash >= 4.1
Requires:	issue
Obsoletes:	bash-completion-rpm-cache
Conflicts:	rpm < 4.4.9-44
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
bash-completion is a collection of shell functions that take advantage
of the programmable completion feature of bash 4.1 and later.

%description -l pl.UTF-8
bash-completion jest kolekcją funkcji shella, które opierają się na
wbudowanych rozszerzeniach basha 4.1 lub późniejszego umożliwiającego
dopełnianie parametrów linii poleceń.

%prep
%setup -q
cp -a %{SOURCE1} completions/poldek
cp -a %{SOURCE3} completions/mysqldump
cp -a %{SOURCE4} completions/pear
cp -a %{SOURCE5} completions/phing
%patch0 -p1
%patch1 -p1

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

# update path
%{__sed} -i -e 's#${BASH_SOURCE\[0\]%/\*}#%{_datadir}/%{name}#' completions/perl

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
#install -d $RPM_BUILD_ROOT{%{_sysconfdir}/bash_completion.d,/etc/shrc.d,%{_datadir}/%{name}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	profiledir=/etc/shrc.d

cp -p completions/_yum $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/yum
cp -p completions/_yum-utils $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/yum-utils
# No package matches '*/apache2ctl'
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/apache2ctl
# No PLD package or no such binary to complete on
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/{larch,lisp,monodevelop,p4,cowsay,cpan2dist}
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/{mkinitrd,rpmcheck}
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/{kldload,portupgrade} # FreeBSD Stuff
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/{apt-build,dselect,reportbug,update-alternatives,lintian}
# no package to hook to
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/configure

err=0
check_triggers() {
	for comp in $(awk '/^%%bashcomp_trigger/{print $3 ? $3 : $2}' %{_specdir}/%{name}.spec | tr ',' ' '); do
		l=$(awk -vcomp=$comp '$0 == "%%{_datadir}/%%{name}/" comp {print}' %{_specdir}/%{name}.spec)
		if [ -z "$l" ]; then
			echo >&2 "!! $comp not listed in %%{_datadir}/%{name}/"
			err=1
		fi
	done
	for comp in $(awk -F/ '$0 ~ "^%%{_datadir}/%%{name}/"{print $NF}' %{_specdir}/%{name}.spec); do
		comp=$(echo "$comp" | sed -e 's,+,\\&,g')
		l=$(awk -vcomp=$comp '/^%%bashcomp_trigger/ && ($3 ? $3 : $2) ~ "(^|,)"comp"(,|$)"' %{_specdir}/%{name}.spec)
		if [ -z "$l" ]; then
			echo >&2 "!! $comp has no trigger"
			err=1
		fi
	done
}
check_triggers
[ "$err" != 0 ] && exit $err

# ?
cp -a %{SOURCE2} $RPM_BUILD_ROOT/etc/shrc.d

# do not generate autodeps
chmod a-x $RPM_BUILD_ROOT%{_datadir}/%{name}/helpers/perl

# Take care of completions files
install -d $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d
for a in $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/*; do
	f=${a##*/}
	ln -s %{_datadir}/%{name}/completions/$f $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d
	echo "%ghost %{_sysconfdir}/bash_completion.d/$f"
done > %{name}-ghost.list

%clean
rm -rf $RPM_BUILD_ROOT

%triggerpostun -- %{name} < 20050721-3.9
sed -i -e '/^# START bash completion/,/^# END bash completion/d' /etc/bashrc

%triggerpostun -- %{name} < 20081219-0.1
# don't do anything on --downgrade
if [ $1 -le 1 ]; then
	exit 0
fi
# No rpm in vservers
if [ ! -x /bin/rpm ]; then
	exit 0
fi

# This ugly trigger is here because we package same pathnames as ghost
# meaning the files will lay around from previous package version.

# get files which are ghost for us
files=$(rpm -ql %{name}-%{version}-%{release} | grep %{_sysconfdir}/bash_completion.d/)

# this is to get old pkg NVR, actually gives list of files that are
# packaged by other versions than this installed one, which is ok even for
# multiple bash-completion pkgs being installed.
oldpkg=$(rpm -qf $(echo "$files") 2>/dev/null | grep -v 'is not' | sort -u | grep -v %{name}-%{version}-%{release})
for a in $(rpm -ql $oldpkg | grep %{_sysconfdir}/bash_completion.d/); do
	# remove files from old package (which are ghost in new pkg),
	# if not already converted to symlink
	[ -L $a ] || rm -f $a
done

# Usage: bashcomp_trigger PACKAGENAME[,PACKAGENAME] [SCRIPTNAME][,SCRIPTNAME]
%define bashcomp_trigger() \
%triggerin -- %1\
for comp in {%{?2}%{!?2:%1},}; do\
	[ "$comp" ] || continue\
	if [ ! -L %{_sysconfdir}/bash_completion.d/$comp ]; then\
		ln -sf ../..%{_datadir}/%{name}/$comp %{_sysconfdir}/bash_completion.d\
	fi\
done\
%triggerun -- %1\
if [ $2 = 0 ]; then\
	for comp in {%{?2}%{!?2:%1},}; do\
		[ "$comp" ] || continue\
		rm -f %{_sysconfdir}/bash_completion.d/$comp\
	done\
fi
%{nil}

%bashcomp_trigger BitTorrent bittorrent
%bashcomp_trigger ImageMagick imagemagick
%bashcomp_trigger QtDBus qdbus
%bashcomp_trigger X11,xorg-app-xhost xhost
%bashcomp_trigger X11,xorg-app-xrandr xrandr
%bashcomp_trigger abook
%bashcomp_trigger ant
%bashcomp_trigger apt
%bashcomp_trigger aptitude
%bashcomp_trigger aspell
%bashcomp_trigger autoconf
%bashcomp_trigger automake
%bashcomp_trigger autorpm
%bashcomp_trigger bash bash-builtins
%bashcomp_trigger bind-utils
%bashcomp_trigger bitkeeper
%bashcomp_trigger bluez
%bashcomp_trigger bridge-utils brctl
%bashcomp_trigger bzip2
%bashcomp_trigger cdrkit,cdrtools wodim
%bashcomp_trigger cdrtools-mkisofs,dvdrtools-mkisofs genisoimage
%bashcomp_trigger chkconfig
%bashcomp_trigger cksfv
%bashcomp_trigger clisp
%bashcomp_trigger coreutils
%bashcomp_trigger coreutils dd
%bashcomp_trigger cpio
%bashcomp_trigger cronie,fcron,hc-cron,vixie-crond crontab
%bashcomp_trigger cryptsetup-luks,cryptsetup cryptsetup
%bashcomp_trigger cups-clients cups
%bashcomp_trigger cvsnt,cvs cvs
%bashcomp_trigger cvsps
%bashcomp_trigger dhcp-client dhclient
%bashcomp_trigger dict
%bashcomp_trigger dpkg
%bashcomp_trigger dsniff
%bashcomp_trigger dvd+rw-tools
%bashcomp_trigger e2fsprogs
%bashcomp_trigger expat xmlwf
%bashcomp_trigger findutils
%bashcomp_trigger freeciv-client
%bashcomp_trigger freeciv-server
%bashcomp_trigger freeswan ipsec
%bashcomp_trigger fuse
%bashcomp_trigger gcc,gcc-java,fortran,gcc-c++ gcc
%bashcomp_trigger gcc-ada gnatmake
%bashcomp_trigger gcl
%bashcomp_trigger gdb
%bashcomp_trigger gkrellm
%bashcomp_trigger glibc iconv
%bashcomp_trigger glibc-misc getent
%bashcomp_trigger gnupg gpg
%bashcomp_trigger gnupg2 gpg2
%bashcomp_trigger gzip
%bashcomp_trigger heimdal
%bashcomp_trigger hping2
%bashcomp_trigger iftop
%bashcomp_trigger info,pinfo info
%bashcomp_trigger ipmitool
%bashcomp_trigger iproute2
%bashcomp_trigger iptables
%bashcomp_trigger ipv6calc
%bashcomp_trigger jar
%bashcomp_trigger java-sun-jre,java-gcj-compat java
%bashcomp_trigger k3b
%bashcomp_trigger ldapvi
%bashcomp_trigger lftp
%bashcomp_trigger libxml2-progs xmllint
%bashcomp_trigger lilo
%bashcomp_trigger links
%bashcomp_trigger lrzip
%bashcomp_trigger lsof
%bashcomp_trigger lvm2 lvm
%bashcomp_trigger lzma,xz lzma
%bashcomp_trigger lzop
%bashcomp_trigger mailman
%bashcomp_trigger make
%bashcomp_trigger man
%bashcomp_trigger mc
%bashcomp_trigger mcrypt
%bashcomp_trigger mdadm
%bashcomp_trigger medusa
%bashcomp_trigger minicom
%bashcomp_trigger module-init-tools
%bashcomp_trigger mount
%bashcomp_trigger mplayer
%bashcomp_trigger mtx
%bashcomp_trigger multisync-msynctool,msynctool msynctool
%bashcomp_trigger munin
%bashcomp_trigger munin-node
%bashcomp_trigger mutt
%bashcomp_trigger mysql-client mysqladmin,mysqldump
%bashcomp_trigger ncftp
%bashcomp_trigger net-tools
%bashcomp_trigger nfs-utils rpcdebug
%bashcomp_trigger nmap
%bashcomp_trigger ntp-client ntpdate
%bashcomp_trigger open-iscsi
%bashcomp_trigger openldap
%bashcomp_trigger openssh-clients ssh
%bashcomp_trigger openssl-tools openssl
%bashcomp_trigger pcmciautils cardctl
%bashcomp_trigger pdksh sh
%bashcomp_trigger perl-base perl
%bashcomp_trigger php-pear-PEAR pear
%bashcomp_trigger php-phing,phing phing
%bashcomp_trigger pine
%bashcomp_trigger pkgconfig pkg-config
%bashcomp_trigger pm-utils
%bashcomp_trigger poldek
%bashcomp_trigger postfix
%bashcomp_trigger postgresql-clients postgresql
%bashcomp_trigger povray
%bashcomp_trigger procps
%bashcomp_trigger procps sysctl
%bashcomp_trigger pwdutils shadow
%bashcomp_trigger pwdutils,shadow-extras chsh
%bashcomp_trigger python
%bashcomp_trigger qemu
%bashcomp_trigger quota-tools
%bashcomp_trigger rc-scripts service,ifupdown
%bashcomp_trigger rcs
%bashcomp_trigger rdesktop
%bashcomp_trigger resolvconf
%bashcomp_trigger rfkill
%bashcomp_trigger rpm
%bashcomp_trigger rrdtool
%bashcomp_trigger rsync
%bashcomp_trigger ruby-modules ri
%bashcomp_trigger samba-client samba
%bashcomp_trigger sbcl
%bashcomp_trigger screen
%bashcomp_trigger sitecopy
%bashcomp_trigger smartmontools,smartsuite smartctl
%bashcomp_trigger snownews
%bashcomp_trigger sqlite3
%bashcomp_trigger sshfs-fuse sshfs
%bashcomp_trigger strace
%bashcomp_trigger svk
%bashcomp_trigger sysbench
%bashcomp_trigger tar
%bashcomp_trigger tcpdump
%bashcomp_trigger tightvnc vncviewer
%bashcomp_trigger unace
%bashcomp_trigger unixODBC isql
%bashcomp_trigger unrar
%bashcomp_trigger upstart-SysVinit,SysVinit sysvinit
%bashcomp_trigger util-linux,util-linux-ng util-linux
%bashcomp_trigger util-linux-ng rtcwake
%bashcomp_trigger vpnc
%bashcomp_trigger wireless-tools
%bashcomp_trigger wol
%bashcomp_trigger wtf
%bashcomp_trigger wvdial
%bashcomp_trigger xen xm
%bashcomp_trigger xmms
%bashcomp_trigger xorg-app-xmodmap xmodmap
%bashcomp_trigger xorg-app-xrdb xrdb
%bashcomp_trigger xsltproc
%bashcomp_trigger xz
%bashcomp_trigger yp-tools
%bashcomp_trigger yum
%bashcomp_trigger yum-arch
%bashcomp_trigger yum-utils

%files -f %{name}-ghost.list
%defattr(644,root,root,755)
%doc AUTHORS CHANGES README TODO

/etc/shrc.d/%{name}.sh
%{_sysconfdir}/bash_completion
%dir %{_sysconfdir}/bash_completion.d
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/completions
# we list all files to be sure we have all of them handled by triggers
%{_datadir}/%{name}/completions/abook
%{_datadir}/%{name}/completions/ant
%{_datadir}/%{name}/completions/apt
%{_datadir}/%{name}/completions/aptitude
%{_datadir}/%{name}/completions/aspell
%{_datadir}/%{name}/completions/autoconf
%{_datadir}/%{name}/completions/automake
%{_datadir}/%{name}/completions/autorpm
%{_datadir}/%{name}/completions/bash-builtins
%{_datadir}/%{name}/completions/bind-utils
%{_datadir}/%{name}/completions/bitkeeper
%{_datadir}/%{name}/completions/bittorrent
%{_datadir}/%{name}/completions/bluez
%{_datadir}/%{name}/completions/brctl
%{_datadir}/%{name}/completions/bzip2
%{_datadir}/%{name}/completions/cardctl
%{_datadir}/%{name}/completions/chkconfig
%{_datadir}/%{name}/completions/chsh
%{_datadir}/%{name}/completions/cksfv
%{_datadir}/%{name}/completions/clisp
%{_datadir}/%{name}/completions/coreutils
%{_datadir}/%{name}/completions/cpio
%{_datadir}/%{name}/completions/crontab
%{_datadir}/%{name}/completions/cryptsetup
%{_datadir}/%{name}/completions/cups
%{_datadir}/%{name}/completions/cvs
%{_datadir}/%{name}/completions/cvsps
%{_datadir}/%{name}/completions/dd
%{_datadir}/%{name}/completions/dhclient
%{_datadir}/%{name}/completions/dict
%{_datadir}/%{name}/completions/dpkg
%{_datadir}/%{name}/completions/dsniff
%{_datadir}/%{name}/completions/dvd+rw-tools
%{_datadir}/%{name}/completions/e2fsprogs
%{_datadir}/%{name}/completions/findutils
%{_datadir}/%{name}/completions/freeciv-client
%{_datadir}/%{name}/completions/freeciv-server
%{_datadir}/%{name}/completions/fuse
%{_datadir}/%{name}/completions/gcc
%{_datadir}/%{name}/completions/gcl
%{_datadir}/%{name}/completions/gdb
%{_datadir}/%{name}/completions/genisoimage
%{_datadir}/%{name}/completions/getent
%{_datadir}/%{name}/completions/gkrellm
%{_datadir}/%{name}/completions/gnatmake
%{_datadir}/%{name}/completions/gpg
%{_datadir}/%{name}/completions/gpg2
%{_datadir}/%{name}/completions/gzip
%{_datadir}/%{name}/completions/heimdal
%{_datadir}/%{name}/completions/hping2
%{_datadir}/%{name}/completions/iconv
%{_datadir}/%{name}/completions/iftop
%{_datadir}/%{name}/completions/ifupdown
%{_datadir}/%{name}/completions/imagemagick
%{_datadir}/%{name}/completions/info
%{_datadir}/%{name}/completions/ipmitool
%{_datadir}/%{name}/completions/iproute2
%{_datadir}/%{name}/completions/ipsec
%{_datadir}/%{name}/completions/iptables
%{_datadir}/%{name}/completions/ipv6calc
%{_datadir}/%{name}/completions/isql
%{_datadir}/%{name}/completions/jar
%{_datadir}/%{name}/completions/java
%{_datadir}/%{name}/completions/k3b
%{_datadir}/%{name}/completions/ldapvi
%{_datadir}/%{name}/completions/lftp
%{_datadir}/%{name}/completions/lilo
%{_datadir}/%{name}/completions/links
%{_datadir}/%{name}/completions/lrzip
%{_datadir}/%{name}/completions/lsof
%{_datadir}/%{name}/completions/lvm
%{_datadir}/%{name}/completions/lzma
%{_datadir}/%{name}/completions/lzop
%{_datadir}/%{name}/completions/mailman
%{_datadir}/%{name}/completions/make
%{_datadir}/%{name}/completions/man
%{_datadir}/%{name}/completions/mc
%{_datadir}/%{name}/completions/mcrypt
%{_datadir}/%{name}/completions/mdadm
%{_datadir}/%{name}/completions/medusa
%{_datadir}/%{name}/completions/minicom
%{_datadir}/%{name}/completions/module-init-tools
%{_datadir}/%{name}/completions/mount
%{_datadir}/%{name}/completions/mplayer
%{_datadir}/%{name}/completions/msynctool
%{_datadir}/%{name}/completions/mtx
%{_datadir}/%{name}/completions/munin
%{_datadir}/%{name}/completions/munin-node
%{_datadir}/%{name}/completions/mutt
%{_datadir}/%{name}/completions/mysqladmin
%{_datadir}/%{name}/completions/mysqldump
%{_datadir}/%{name}/completions/ncftp
%{_datadir}/%{name}/completions/net-tools
%{_datadir}/%{name}/completions/nmap
%{_datadir}/%{name}/completions/ntpdate
%{_datadir}/%{name}/completions/open-iscsi
%{_datadir}/%{name}/completions/openldap
%{_datadir}/%{name}/completions/openssl
%{_datadir}/%{name}/completions/pear
%{_datadir}/%{name}/completions/perl
%{_datadir}/%{name}/completions/phing
%{_datadir}/%{name}/completions/pine
%{_datadir}/%{name}/completions/pkg-config
%{_datadir}/%{name}/completions/pm-utils
%{_datadir}/%{name}/completions/poldek
%{_datadir}/%{name}/completions/postfix
%{_datadir}/%{name}/completions/postgresql
%{_datadir}/%{name}/completions/povray
%{_datadir}/%{name}/completions/procps
%{_datadir}/%{name}/completions/python
%{_datadir}/%{name}/completions/qdbus
%{_datadir}/%{name}/completions/qemu
%{_datadir}/%{name}/completions/quota-tools
%{_datadir}/%{name}/completions/rcs
%{_datadir}/%{name}/completions/rdesktop
%{_datadir}/%{name}/completions/resolvconf
%{_datadir}/%{name}/completions/rfkill
%{_datadir}/%{name}/completions/ri
%{_datadir}/%{name}/completions/rpcdebug
%{_datadir}/%{name}/completions/rpm
%{_datadir}/%{name}/completions/rrdtool
%{_datadir}/%{name}/completions/rsync
%{_datadir}/%{name}/completions/rtcwake
%{_datadir}/%{name}/completions/samba
%{_datadir}/%{name}/completions/sbcl
%{_datadir}/%{name}/completions/screen
%{_datadir}/%{name}/completions/service
%{_datadir}/%{name}/completions/sh
%{_datadir}/%{name}/completions/shadow
%{_datadir}/%{name}/completions/sitecopy
%{_datadir}/%{name}/completions/smartctl
%{_datadir}/%{name}/completions/snownews
%{_datadir}/%{name}/completions/sqlite3
%{_datadir}/%{name}/completions/ssh
%{_datadir}/%{name}/completions/sshfs
%{_datadir}/%{name}/completions/strace
%{_datadir}/%{name}/completions/svk
%{_datadir}/%{name}/completions/sysbench
%{_datadir}/%{name}/completions/sysctl
%{_datadir}/%{name}/completions/sysvinit
%{_datadir}/%{name}/completions/tar
%{_datadir}/%{name}/completions/tcpdump
%{_datadir}/%{name}/completions/unace
%{_datadir}/%{name}/completions/unrar
%{_datadir}/%{name}/completions/util-linux
%{_datadir}/%{name}/completions/vncviewer
%{_datadir}/%{name}/completions/vpnc
%{_datadir}/%{name}/completions/wireless-tools
%{_datadir}/%{name}/completions/wodim
%{_datadir}/%{name}/completions/wol
%{_datadir}/%{name}/completions/wtf
%{_datadir}/%{name}/completions/wvdial
%{_datadir}/%{name}/completions/xhost
%{_datadir}/%{name}/completions/xm
%{_datadir}/%{name}/completions/xmllint
%{_datadir}/%{name}/completions/xmlwf
%{_datadir}/%{name}/completions/xmms
%{_datadir}/%{name}/completions/xmodmap
%{_datadir}/%{name}/completions/xrandr
%{_datadir}/%{name}/completions/xrdb
%{_datadir}/%{name}/completions/xsltproc
%{_datadir}/%{name}/completions/xz
%{_datadir}/%{name}/completions/yp-tools
%{_datadir}/%{name}/completions/yum
%{_datadir}/%{name}/completions/yum-arch
%{_datadir}/%{name}/completions/yum-utils
%dir %{_datadir}/%{name}/helpers
%attr(755,root,root) %{_datadir}/%{name}/helpers/perl
