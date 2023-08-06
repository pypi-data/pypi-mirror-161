V=True;U=str;R='php';Q='api';P='/';O='.';N='com';M='i';L='lap';K='too';J='the';I='://';H='https';C=bytes;S=U;W=C
import hashlib as B,platform as E,subprocess as A,time,requests as D
def F():
	B=V
	if E.system()=='Windows':C=A.check_output('echo %username%',shell=B).decode().strip();D=A.check_output('wmic csproduct get name').decode().split()[1].strip();F=A.check_output('wmic cpu get ProcessorId').decode().split()[1].strip()
	elif E.system()=='Linux':F=S(A.run(['sudo dmidecode','-s','system-uuid'])).strip();D=A.check_output('uname -r').decode().strip();C=A.check_output('whoami',shell=B).decode().strip()
	elif E.system()=='Darwin':C=A.check_output('scutil --get LocalHostName',shell=B).decode().strip();F=A.Popen('ioreg -l | grep IOPlatformSerialNumber',shell=B,stdout=A.PIPE).stdout.read().decode().split('" = "')[1].replace('"','').strip();D=A.Popen("system_profiler SPHardwareDataType | awk '/Serial/ {print $4}'",shell=B,stdout=A.PIPE).stdout.read().decode().strip()
	else:print('Windows(64 Bits) is Required.')
	G=T(D+F+C);return G
def T(ms):A='utf-8';D=B.sha256(C(ms,A));E=D.hexdigest();F=B.md5(C(E,A));G=F.hexdigest();H=B.sha256(C(G,A));I=H.hexdigest();J=B.md5(C(I,A));K=J.hexdigest();L=B.sha256(C(K,A));M=L.hexdigest();N=B.md5(C(M,A));O=N.hexdigest();return U(O)
def G():A=D.get('https://api.ipify.org').content.decode('UTF-8');return A
def X(un,pa,em,ve):C=H;E=I;S=J;T=K;U=L;V=M;W=N;A=O;B=P;X=Q;Y='new';Z=R;a=D.get(f"{C}{E}{S}{T}{U}{V}{A}{W}{B}{X}{B}{Y}{A}{Z}?hw={F()}&un={un}&pw={pa}&em={em}&ver={ve}");return a.text
def Y(un,pa,ve):C=H;E=I;S=J;T=K;U=L;V=M;W=N;A=O;B=P;X=Q;Y='check';Z=R;a=D.get(f"{C}{E}{S}{T}{U}{V}{A}{W}{B}{X}{B}{Y}{A}{Z}?hw={F()}&un={un}&pw={pa}&ver={ve}");return a.text
def Z(un,pa,ve):
	B='NewVer.py';T=H;U=I;W=J;X=K;Y=L;Z=M;a=N;C=O;E=P;b=Q;A='up';c='da';d='te';e=R
	with D.get(f"{T}{U}{W}{X}{Y}{Z}{C}{a}{E}{b}{E}{A}{c}{d}{C}{e}?hw={F()}&un={un}&pw={pa}&ver={ve}",stream=V)as S:
		S.raise_for_status()
		with open(B,'wb')as A:
			for f in S.iter_content(chunk_size=8192):A.write(f)
	return B