# vim:ft=spec
# TODO
# - bittorrent complete doesn't actually handle our prognames
# - use mkinitrd and update for geninitrd
Summary:	bash-completion offers programmable completion for bash
Summary(pl.UTF-8):	Programowalne uzupełnianie nazw dla basha
Name:		bash-completion
Version:	1.0
Release:	3
Epoch:		1
License:	GPL
Group:		Applications/Shells
#Source0:	http://bash-completion.alioth.debian.org/files/%{name}-%{version}.tar.gz
Source0:	%{name}.tar.bz2
# Source0-md5:	296df2d2ac8b9826d73ff7d559333023
Source1:	%{name}-poldek.sh
Source2:	%{name}.sh
Patch0:		%{name}-rpm-cache.patch
Patch1:		%{name}-mplayer.patch
Patch2:		%{name}-service.patch
Patch3:		%{name}-psheader.patch
URL:		http://bash-completion.alioth.debian.org/
Requires(triggerpostun):	sed >= 4.0
Requires:	bash >= 2.05a-3
Obsoletes:	bash-completion-rpm-cache
Conflicts:	rpm < 4.4.9-44
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
bash-completion is a collection of shell functions that take advantage
of the programmable completion feature of bash 2.04 and later.

%description -l pl.UTF-8
bash-completion jest kolekcją funkcji shella, które opierają się na
wbudowanych rozszerzeniach basha 2.04 lub późniejszego umożliwiającego
kompletowanie parametrów linii poleceń.

%prep
%setup -q -n %{name}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
cp -a %{SOURCE1} contrib/poldek

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

# packaged by subversion.spec
rm contrib/_subversion

# No package matches '*/apache2ctl'
rm contrib/apache2ctl

# No PLD package or no such binary to complete on
rm contrib/{harbour,larch,lisp,modules,monodevelop,p4,cowsay,cpan2dist}
rm contrib/{cfengine,mkinitrd,repomanage,rpmcheck}

# split freeciv-client,freeciv-server as we have these in separate packages
mv contrib/freeciv .
%{__sed} -ne '1,/complete -F _civserver civserver/p' freeciv > contrib/freeciv-server
%{__sed} -ne '1,3p;/civclient/,$p' freeciv > contrib/freeciv-client
if [ $(md5sum freeciv | awk '{print $1}') != "eb862866780086f264eb4afe1418f3a4" ]; then
	: check that split out contrib/freeciv-{client,server} are ok and update md5sum
	exit 1
fi

# split munin as we have subpackage for node
mv contrib/munin-node .
%{__sed} -ne '1,/complete -F _munin-update munin-update/p' munin-node > contrib/munin
%{__sed} -ne '1,3p;/munin-node-configure/,$p' munin-node > contrib/munin-node
if [ $(md5sum munin-node | awk '{print $1}') != "c51fd6354ee73c1bf34915bc4aaa3856" ]; then
	: check that split out contrib/munin{,-node} are ok and update md5sum
	exit 1
fi

# we have lastlog in sysvinit package
mv contrib/shadow .
%{__sed} -ne '1,/complete -F _faillog faillog/p' shadow > contrib/shadow
%{__sed} -ne '1,3p;/lastlog/,$p' shadow > contrib/sysvinit
if [ $(md5sum shadow | awk '{print $1}') != "4dfef3151921fd9644566a3244038f85" ]; then
	: check that split out contrib/{shadow,sysvinit} are ok and update md5sum
	exit 1
fi

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/bash_completion.d,/etc/shrc.d,%{_datadir}/%{name}}

T=$(grep -c '^%%bashcomp_trigger' %{_specdir}/%{name}.spec)
F=$(grep -c '^%%{_datadir}/%%{name}/' %{_specdir}/%{name}.spec)
if [ $T != $F ]; then
	check_triggers() {
		echo >&2 "ERROR: triggers count and packaged files mismatch"
		for f in $(awk '/^%%bashcomp_trigger/{print $3 ? $3 : $2}' %{_specdir}/%{name}.spec); do
			A=$(awk -vf=$f '$0 == "%%{_datadir}/%%{name}/" f {print}' %{_specdir}/%{name}.spec)
			if [ -z "$A" ]; then
				echo >&2 "!! $f not listed in %%files"
			fi
		done
		for f in $(awk -F/ '$0 ~ "^%%{_datadir}/%%{name}/"{print $NF}' %{_specdir}/%{name}.spec); do
			A=$(awk -vf=$f '/^%%bashcomp_trigger/ && ($3 ? $3 : $2) == f' %{_specdir}/%{name}.spec)
			if [ -z "$A" ]; then
				echo >&2 "!! $f has no trigger"
			fi
		done
	}
	check_triggers
	exit 1
fi

cp -a bash_completion $RPM_BUILD_ROOT%{_sysconfdir}
cp -a contrib/* $RPM_BUILD_ROOT%{_datadir}/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/shrc.d

# Take care of contrib files
for a in contrib/*; do
	f=${a##*/}
	ln -s ../..%{_datadir}/%{name}/$f $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d
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

# Usage: bashcomp_trigger PACKAGENAME [SCRIPTNAME]
%define bashcomp_trigger() \
%triggerin -- %1\
if [ ! -L %{_sysconfdir}/bash_completion.d/%{?2}%{!?2:%1} ] ; then\
	ln -sf ../..%{_datadir}/%{name}/%{?2}%{!?2:%1} %{_sysconfdir}/bash_completion.d\
fi\
%triggerun -- %1\
[ $2 -gt 0 ] || rm -f %{_sysconfdir}/bash_completion.d/%{?2}%{!?2:%1}\
%{nil}

%bashcomp_trigger ant
%bashcomp_trigger bind-utils
%bashcomp_trigger bitkeeper
%bashcomp_trigger BitTorrent bittorrent
%bashcomp_trigger bluez bluez-utils
%bashcomp_trigger bridge-utils brctl
%bashcomp_trigger bzip2
%bashcomp_trigger cdrkit,cdrtools wodim
%bashcomp_trigger cdrtools-mkisofs,dvdrtools-mkisofs genisoimage
%bashcomp_trigger cksfv
%bashcomp_trigger clisp
%bashcomp_trigger coreutils dd
%bashcomp_trigger cpio
%bashcomp_trigger dhcp-client dhclient
%bashcomp_trigger dsniff
%bashcomp_trigger findutils
%bashcomp_trigger freeciv-client
%bashcomp_trigger freeciv-server
%bashcomp_trigger gcc-ada gnatmake
%bashcomp_trigger gcl
%bashcomp_trigger gdb
%bashcomp_trigger gkrellm
%bashcomp_trigger glibc-misc getent
%bashcomp_trigger gnupg2 gpg2
%bashcomp_trigger gzip
%bashcomp_trigger heimdal
%bashcomp_trigger ImageMagick imagemagick
%bashcomp_trigger ldapvi
%bashcomp_trigger lftp
%bashcomp_trigger libxml2-progs xmllint
%bashcomp_trigger lilypond
%bashcomp_trigger lvm2 lvm
%bashcomp_trigger lzma,xz lzma
%bashcomp_trigger lzop
%bashcomp_trigger mailman
%bashcomp_trigger make
%bashcomp_trigger mc
%bashcomp_trigger mcrypt
%bashcomp_trigger minicom
%bashcomp_trigger mplayer
%bashcomp_trigger mtx
%bashcomp_trigger multisync-msynctool,msynctool msynctool
%bashcomp_trigger munin
%bashcomp_trigger munin-node
%bashcomp_trigger mysql-client mysqladmin
%bashcomp_trigger ncftp
%bashcomp_trigger net-tools
%bashcomp_trigger nfs-utils rpcdebug
%bashcomp_trigger ntp-client ntpdate
%bashcomp_trigger openldap
%bashcomp_trigger openssh-clients ssh
%bashcomp_trigger openssl-tools openssl
%bashcomp_trigger pkgconfig pkg-config
%bashcomp_trigger poldek
%bashcomp_trigger postfix
%bashcomp_trigger postgresql-clients postgresql
%bashcomp_trigger povray
%bashcomp_trigger pwdutils shadow
%bashcomp_trigger qemu
%bashcomp_trigger QtDBus qdbus
%bashcomp_trigger quota-tools
%bashcomp_trigger rdesktop
%bashcomp_trigger rsync
%bashcomp_trigger ruby-modules ri
%bashcomp_trigger samba-client samba
%bashcomp_trigger sbcl
%bashcomp_trigger screen
%bashcomp_trigger sitecopy
%bashcomp_trigger smartmontools,smartsuite smartctl
%bashcomp_trigger snownews
%bashcomp_trigger strace
%bashcomp_trigger svk
%bashcomp_trigger tar
%bashcomp_trigger tightvnc vncviewer
%bashcomp_trigger unace
%bashcomp_trigger unixODBC isql
%bashcomp_trigger unrar
%bashcomp_trigger upstart-SysVinit,SysVinit sysvinit
%bashcomp_trigger vpnc
%bashcomp_trigger X11,xorg-app-xhost xhost
%bashcomp_trigger xen xm
%bashcomp_trigger xmms
%bashcomp_trigger yum

%files -f %{name}-ghost.list
%defattr(644,root,root,755)
%doc README TODO
/etc/shrc.d/%{name}.sh
%{_sysconfdir}/bash_completion
%dir %{_sysconfdir}/bash_completion.d
%dir %{_datadir}/%{name}
# we list all files to be sure we have all of them handled by triggers
%{_datadir}/%{name}/ant
%{_datadir}/%{name}/bind-utils
%{_datadir}/%{name}/bitkeeper
%{_datadir}/%{name}/bittorrent
%{_datadir}/%{name}/bluez-utils
%{_datadir}/%{name}/brctl
%{_datadir}/%{name}/bzip2
%{_datadir}/%{name}/cksfv
%{_datadir}/%{name}/clisp
%{_datadir}/%{name}/cpio
%{_datadir}/%{name}/dd
%{_datadir}/%{name}/dhclient
%{_datadir}/%{name}/dsniff
%{_datadir}/%{name}/findutils
%{_datadir}/%{name}/freeciv-client
%{_datadir}/%{name}/freeciv-server
%{_datadir}/%{name}/gcl
%{_datadir}/%{name}/gdb
%{_datadir}/%{name}/genisoimage
%{_datadir}/%{name}/getent
%{_datadir}/%{name}/gkrellm
%{_datadir}/%{name}/gnatmake
%{_datadir}/%{name}/gpg2
%{_datadir}/%{name}/gzip
%{_datadir}/%{name}/heimdal
%{_datadir}/%{name}/imagemagick
%{_datadir}/%{name}/isql
%{_datadir}/%{name}/ldapvi
%{_datadir}/%{name}/lftp
%{_datadir}/%{name}/lilypond
%{_datadir}/%{name}/lvm
%{_datadir}/%{name}/lzma
%{_datadir}/%{name}/lzop
%{_datadir}/%{name}/mailman
%{_datadir}/%{name}/make
%{_datadir}/%{name}/mc
%{_datadir}/%{name}/mcrypt
%{_datadir}/%{name}/minicom
%{_datadir}/%{name}/mplayer
%{_datadir}/%{name}/msynctool
%{_datadir}/%{name}/mtx
%{_datadir}/%{name}/munin
%{_datadir}/%{name}/munin-node
%{_datadir}/%{name}/mysqladmin
%{_datadir}/%{name}/ncftp
%{_datadir}/%{name}/net-tools
%{_datadir}/%{name}/ntpdate
%{_datadir}/%{name}/openldap
%{_datadir}/%{name}/openssl
%{_datadir}/%{name}/pkg-config
%{_datadir}/%{name}/poldek
%{_datadir}/%{name}/postfix
%{_datadir}/%{name}/postgresql
%{_datadir}/%{name}/povray
%{_datadir}/%{name}/qdbus
%{_datadir}/%{name}/qemu
%{_datadir}/%{name}/quota-tools
%{_datadir}/%{name}/rdesktop
%{_datadir}/%{name}/ri
%{_datadir}/%{name}/rpcdebug
%{_datadir}/%{name}/rsync
%{_datadir}/%{name}/samba
%{_datadir}/%{name}/sbcl
%{_datadir}/%{name}/screen
%{_datadir}/%{name}/shadow
%{_datadir}/%{name}/sitecopy
%{_datadir}/%{name}/smartctl
%{_datadir}/%{name}/snownews
%{_datadir}/%{name}/ssh
%{_datadir}/%{name}/strace
%{_datadir}/%{name}/svk
%{_datadir}/%{name}/sysvinit
%{_datadir}/%{name}/tar
%{_datadir}/%{name}/unace
%{_datadir}/%{name}/unrar
%{_datadir}/%{name}/vncviewer
%{_datadir}/%{name}/vpnc
%{_datadir}/%{name}/wodim
%{_datadir}/%{name}/xhost
%{_datadir}/%{name}/xm
%{_datadir}/%{name}/xmllint
%{_datadir}/%{name}/xmms
%{_datadir}/%{name}/yum
