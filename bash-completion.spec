Summary:	bash-completion offers programmable completion for bash
Summary(pl):	Programowalne uzupe³nianie nazw dla basha
Name:		bash-completion
Version:	20041017
Release:	1
License:	GPL
Group:		Applications/Shells
Source0:	http://www.caliban.org/files/bash/%{name}-%{version}.tar.bz2
# Source0-md5:	3fd0836127d01606a9dc4262f3e2e1fb
# Source0-size:	86227
URL:		http://www.caliban.org/bash/
Requires(post,preun):	bash
Requires(post):	grep
Requires(post):	textutils
Requires(postun):	fileutils
Requires(postun):	sed
BuildArch:	noarch
Requires:	bash >= 2.05a-3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
bash-completion is a collection of shell functions that take advantage
of the programmable completion feature of bash 2.04 and later.

%description -l pl
bash-completion jest kolekcj± funkcji shella, które opieraj± siê na
wbudowanych rozszerzeniach basha 2.04 lub pó¼niejszego umo¿liwiaj±cego
kompletowanie parametrów linii poleceñ.

%prep
%setup -q -n bash_completion

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d

install bash_completion $RPM_BUILD_ROOT%{_sysconfdir}
install contrib/*       $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d

# subversion comes with much better completion file
rm $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/subversion

%clean
rm -rf $RPM_BUILD_ROOT

%post
if ! grep -q '\[ -f '%{_sysconfdir}'/bash_completion \]' \
	%{_sysconfdir}/bashrc 2>/dev/null; then
		umask 022
		cat <<'EOF' >> %{_sysconfdir}/bashrc
# START bash completion -- do not remove this line
bash=${BASH_VERSION%.*}; bmajor=${bash%.*}; bminor=${bash#*.}
if [ "$bmajor" -eq 2 -a "$bminor" '>' 04 ] || [ "$bmajor" -gt 2 ]; then
	if [ "$PS1" ] && [ -f %{_sysconfdir}/bash_completion ]; then # interactive shell
		# Source completion code
		. %{_sysconfdir}/bash_completion
	fi
fi
unset bash bmajor bminor
# END bash completion -- do not remove this line
EOF
fi

%postun
if [ "$1" -eq 0 ]; then
	umask 022
	sed -e '/^# START bash completion/,/^# END bash completion/d' /etc/bashrc \
		> /etc/bashrc.tmp
	mv -f /etc/bashrc.tmp /etc/bashrc
fi

%files
%defattr(644,root,root,755)
%doc README Changelog BUGS
%{_sysconfdir}/bash_completion
%{_sysconfdir}/bash_completion.d/
