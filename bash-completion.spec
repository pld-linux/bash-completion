%define bashversion 2.05a
Summary:	bash-completion offers programmable completion for bash %{bashversion}
Summary(pl):	Programowalne uzupe³nianie nazw dla basha %{bashversion}
Name:		bash-completion
Version:	20020427
Release:	1
Group:		Applications/Shells
License:	GPL
Source0:	http://www.caliban.org/files/bash/%{name}-%{version}.tar.bz2
URL:		http://www.caliban.org/bash/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
BuildArch:	noarch
Requires:	bash >= %{bashversion}-3
Requires(post):	grep
Requires(postun): sed

%description
bash-completion is a collection of shell functions that take advantage
of the programmable completion feature of bash 2.04 and later. To use
this collection, you ideally need bash 2.05a or later.

%description -l pl
bash-completion jest kolekcj± funkcji shella, które opieraj± siê na
wbudowanych rozszerzeniach basha 2.04 lub pó¼niejszego. Aby u¿ywaæ tej
kolekcji, potrzebujesz basha 2.05a lub pó¼niejszego.

%prep
%setup -q -n bash_completion

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}
install bash_completion $RPM_BUILD_ROOT%{_sysconfdir}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d

gzip -9nf README Changelog

%clean
rm -rf $RPM_BUILD_ROOT

%post
if ! grep -q '\[ -f '%{_sysconfdir}'/bash_completion \]' \
     %{_sysconfdir}/bashrc 2>/dev/null; then
    cat <<'EOF' >> %{_sysconfdir}/bashrc
# START bash completion -- do not remove this line
bash=${BASH_VERSION%.*}; bmajor=${bash%.*}; bminor=${bash#*.}
if [ "$PS1" ] && [ "$bmajor" -eq 2 ] && [ "$bminor" '>' 04 ] \
   && [ -f %{_sysconfdir}/bash_completion ]; then	# interactive shell
	# Source completion code
        . %{_sysconfdir}/bash_completion
fi
unset bash bmajor bminor
# END bash completion -- do not remove this line
EOF
fi

%postun
if [ "$1" -eq 0 ]; then
    sed -e '/^# START bash completion/,/^# END bash completion/d' /etc/bashrc \
	> /etc/bashrc.tmp
    mv -f /etc/bashrc.tmp /etc/bashrc
fi

%files
%defattr(644,root,root,755)
%{_sysconfdir}/bash_completion
%dir %{_sysconfdir}/bash_completion.d/
%doc *.gz  contrib/
