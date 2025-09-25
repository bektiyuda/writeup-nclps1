
import base64, sys

def _rol8(x, r):
    r &= 7
    x &= 0xFF
    return ((x << r) | (x >> (8 - r))) & 0xFF

class _VM:
    def __init__(self, bytecode, user_input):
        self.bc = bytearray(bytecode)
        self.ip = 0
        self.st = []
        self.s  = [ord(c) & 0xFF for c in user_input]

    def run(self):
        ip = self.ip
        bc = self.bc
        st = self.st
        s  = self.s
        while True:
            op = bc[ip]; ip += 1
            if op == 0x00:
                pass
            elif op == 0x01:
                st.append(bc[ip]); ip += 1
            elif op == 0x02:
                idx = bc[ip]; ip += 1
                st.append(s[idx] if 0 <= idx < len(s) else 0)
            elif op == 0x03:
                b = st.pop(); a = st.pop(); st.append((a ^ b) & 0xFF)
            elif op == 0x04:
                b = st.pop(); a = st.pop(); st.append((a + b) & 0xFF)
            elif op == 0x05:
                r = bc[ip]; ip += 1
                a = st.pop(); st.append(_rol8(a, r))
            elif op == 0x06:
                b = st.pop(); a = st.pop(); st.append(1 if a == b else 0)
            elif op == 0x07:
                b = st.pop(); a = st.pop(); st.append(1 if (a and b) else 0)
            elif op == 0x08:
                return bool(st.pop() if st else 0)
            elif op == 0x09:
                b = st.pop(); a = st.pop(); st.append((a - b) & 0xFF)
            elif op == 0x0A:
                m = bc[ip]; ip += 1
                a = st.pop(); st.append(a % m if m else 0)
            elif op == 0x0B:
                a = st[-1]; st.append(a)
            elif op == 0x0C:
                if st: st.pop()
            else:
                return False

def _dec_blob(b85, key):
    raw = base64.b85decode(b85.encode("ascii"))
    return bytes((b ^ key) & 0xFF for b in raw)

def _main():
    try:
        user = input("Enter license key: ").strip()
    except EOFError:
        print("No input provided."); sys.exit(2)

    if len(user) != 72:
        print("Activation failed."); sys.exit(1)

    bc = _dec_blob('=H&0_<<IBk<mct&;Nj=xYv<)a;^yV==;biy<u>5q;N^7Z<>KPw<mTq(z31iJ;NjxsH|OPK;^XG$@95=i=jDjt;pgR<=jF5F<K*Vx<$34j@!;X$<>u$**y7{l<mTb!nCIpC;Nj=xGw0=K;^XGx<uK>vYT)7G<t*prW8&lH<L~I@CFkY+;Nj)v;OFIK;^XAx=Irn2<<IBk9^m2O<%#Fzfa2rk?eFO2Xy@hG;Nj-wH|OQt;^XG-<vr)+Sm5F2<^Jd8PvYa|@9*g4bLZu?;Nj!t+vnw1;^XG%@95?A=jDOm;o;@i=j9;c<K*P#>F?;}&*$Y@;Njrq=I7;R;^XG(@95?D=jFiQ;o#-*=jEv4<K*P#>*eL=<>BDr=jA--<@Vy^<mBe`@95=p=jAWp;pXL`=jF@d<K*V`<%H+u<mcrf;Nj)vw&&#q;^XAz_V4KB{^#Z7=jD0e;o#+?=jCGJ<L39}73bwv;Njxs`{(7h;^XAx=J4<6<tFFlWZ>cB<>}|;P~zj}@$cy6ndjv{;NjurHRt6>;^XAx=JMq;=jDUo;pXLZ=jC1E<K*V^<u2#t@ZjO$<=5xsVdCTD=KSS5=j9yW;pXLL=jG|*<L3S4LFeU^;NjxsK<DMr;^XAz{^eWe<>cq(vf$z3<*w)DrQ+k{<mUh7N$2H<;Nj)v`{(6r;^XAx=J@4`=jG(*<$>Vg;pHpm<@w^{<mBf0<?`p{<mctn;Nj=xspsXK;^XG}<&Nj&vf$z4<%;L!(Bk9d<mUVD=;gZS<$B=Z<>fQy<qYEE<mBeW@95=<=jAHk;o{|K=j9XP<K*VW<+tbMMBw4(<^1R6BI4ub#^ns><!s>L;N{Kd<%{Cu=Ev{o<uB*uLg3-&<#XrdIpX8w<mSNT`{(84=j9mS;pOGs=jEm1<L1HT7w6^V=jBA;;pOEs=jB)8<L1Ke=;i(A<t*Ug<>l(<<(}f><mSWg=;cf2<tyOf;pJ`T<v8Nw<mSxp=;dzb<pkj2=H=Gs<+$SG<mBef<;dsdCg9=a<*euBl;Y#$<mS%r=;a&d<<#Ke;pKqm<^SU2=FjEy=jG(*<)7f;<K;u=<t*ak<mBea<?ZL?<mcu5;Nj-wndjwr;^XAz$>rnc<>cq(ci`dY<zMIJ0OI53%H?<G<u%~p;pH~x<t*ak<mSuo=;e>+<tE_a<>f)=<$2=c=G5g~=jDjt;pOE-=jG_)<K*Vm<wfV^BH-cT<s|3jhT`Mo<mT4pis$9t;Njur?dRpD;^XGm@95>m=jG(*<u>5q;pMXD<#FQU<mBei@95<k=jG(*<$U1b<K;Z(<tXCg=F#Pz=jG(*<yhe1;pJxM<=*1s=F;Wy=jE8-;pXL>=j9&a<L1-l_~+&1=jHd{;pOGt=jC$Z<K*P#+~t(#<uTyl=j9gX<&om!<mTPwt>@(d;NjrqX6NNV;^XGt<)i22^Wfp*<sRqdzT)HN-{oiL<>cq(?cm|y<!I;S)8gai*yRJ~<zC?7<>l(<<qqQG<mBer@95<#=jG(*<<{Wg<>mV4<wfG-=Gx`u=jFQK;o;@C=jFxX<K*P#+vVlw<>cq(YT)7F<p}5H7UJXN<mRO1Am`<l;Njur<>%!|;^XAzrSItF3FqbH=j93D;pXM+=jHq2<K*V1@95=V=jG(*<+<SD<>jL1<(A^(<mBe3@95=`=jG(*<$~bh;^nmG<rw1Q<mBd{<*euBTj1g2<<95jIO5~v<mRF8=;iC@<;mdT;N?x{<=f)p=Az}U=jD>%;pgR!=jD3h<L0B~E$8Lr=j8<8;pgSY=jCJK<Lm', 228)
    ok = _VM(bc, user).run()
    print("Activation successful." if ok else "Activation failed.")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    _main()
