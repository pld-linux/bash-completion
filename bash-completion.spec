# TODO
# - bittorrent complete doesn't actually handle our prognames
# - handle multiple package links (freeciv case)
# - handle upgrade path to symlinks (see notes in install section)
Summary:	bash-completion offers programmable completion for bash
Summary(pl.UTF-8):	Programowalne uzupełnianie nazw dla basha
Name:		bash-completion
Version:	20081219
Release:	0.12
License:	GPL
Group:		Applications/Shells
Source0:	ftp://distfiles.gentoo.org/pub/gentoo/distfiles/%{name}-%{version}.tar.bz2
# Source0-md5:	6b8f924417fb8cd758778025d97f2853
Source1:	%{name}-poldek.sh
Source2:	%{name}.sh
Patch0:		%{name}-rpm-cache.patch
Patch1:		%{name}-mplayer.patch
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
cp -a %{SOURCE1} contrib/poldek

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

# packaged by subversion.spec
rm contrib/_subversion

# No package matches '*/apache2ctl'
rm contrib/apache2ctl

# No PLD package or no such binary to complete on
rm contrib/{harbour,larch,lisp,modules,monodevelop,p4}

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
	ln -s %{_datadir}/%{name}/$f $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d
	echo "%ghost %{_sysconfdir}/bash_completion.d/$f"
done > %{name}-ghost.list

%clean
rm -rf $RPM_BUILD_ROOT

%triggerpostun -- %{name} < 20050721-3.9
sed -i -e '/^# START bash completion/,/^# END bash completion/d' /etc/bashrc

%triggerpostun -- %{name} < 20081219-0.1
# No rpm in vservers
if [ -x /bin/rpm ]; then
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
fi

# Usage: bashcomp_trigger PACKAGENAME [SCRIPTNAME]
%define bashcomp_trigger() \
%triggerin -- %1\
set -x;\
if [ ! -L %{_sysconfdir}/bash_completion.d/%{?2}%{!?2:%1} ] ; then\
	ln -fs %{_datadir}/%{name}/%{?2}%{!?2:%1} %{_sysconfdir}/bash_completion.d\
fi\
%triggerun -- %1\
set -x;\
[ $2 -gt 0 ] || rm -f %{_sysconfdir}/bash_completion.d/%{?2}%{!?2:%1}\
%{nil}

%bashcomp_trigger bitkeeper
%bashcomp_trigger BitTorrent bittorrent
%bashcomp_trigger cksfv
%bashcomp_trigger clisp
%bashcomp_trigger dsniff
%bashcomp_trigger freeciv-client,freeciv-server freeciv
%bashcomp_trigger gcc-ada gnatmake
%bashcomp_trigger gcl
%bashcomp_trigger gkrellm
%bashcomp_trigger gnupg2 gpg2
%bashcomp_trigger lilypond
%bashcomp_trigger mailman
%bashcomp_trigger mcrypt
%bashcomp_trigger mercurial hg
%bashcomp_trigger mtx
%bashcomp_trigger openssh-clients ssh
%bashcomp_trigger poldek
%bashcomp_trigger povray
%bashcomp_trigger QtDBus qdbus
%bashcomp_trigger ruby-modules ri
%bashcomp_trigger sbcl
%bashcomp_trigger sitecopy
%bashcomp_trigger snownews
%bashcomp_trigger svk
%bashcomp_trigger unace
%bashcomp_trigger unixODBC isql
%bashcomp_trigger unrar

%files -f %{name}-ghost.list
%defattr(644,root,root,755)
%doc README TODO debian/changelog debian/copyright
/etc/shrc.d/%{name}.sh
%{_sysconfdir}/bash_completion
%dir %{_sysconfdir}/bash_completion.d
%dir %{_datadir}/%{name}
# we list all files to be sure we have all of them handled by triggers
%{_datadir}/%{name}/bitkeeper
%{_datadir}/%{name}/bittorrent
%{_datadir}/%{name}/cksfv
%{_datadir}/%{name}/clisp
%{_datadir}/%{name}/dsniff
%{_datadir}/%{name}/freeciv
%{_datadir}/%{name}/gcl
%{_datadir}/%{name}/gkrellm
%{_datadir}/%{name}/gnatmake
%{_datadir}/%{name}/gpg2
%{_datadir}/%{name}/hg
%{_datadir}/%{name}/isql
%{_datadir}/%{name}/lilypond
%{_datadir}/%{name}/mailman
%{_datadir}/%{name}/mcrypt
%{_datadir}/%{name}/mtx
%{_datadir}/%{name}/poldek
%{_datadir}/%{name}/povray
%{_datadir}/%{name}/qdbus
%{_datadir}/%{name}/ri
%{_datadir}/%{name}/sbcl
%{_datadir}/%{name}/sitecopy
%{_datadir}/%{name}/snownews
%{_datadir}/%{name}/ssh
%{_datadir}/%{name}/svk
%{_datadir}/%{name}/unace
%{_datadir}/%{name}/unrar
