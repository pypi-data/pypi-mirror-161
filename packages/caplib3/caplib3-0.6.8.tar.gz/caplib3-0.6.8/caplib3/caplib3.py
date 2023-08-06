#!/usr/bin/env python
__version__='0.6.8'
last_update='2022-08-03'
author='Damien Marsic, damien.marsic@aliyun.com'

import argparse,sys,gzip,math,regex
from glob import glob
import dmbiolib as dbl
import numpy as np
from collections import defaultdict
from collections import Counter
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ambiguous="ryswkmbdhvn"
aa="ARNDCQEGHILKMFPSTWYV"
COLORS=('blue','yellow','lime','red','indigo','peru','deeppink','olive','cyan','teal')

def version():
    print('\n  Project: '+sys.argv[0][max(sys.argv[0].rfind('\\'),sys.argv[0].rfind('/'))+1:-3]+'\n  version: '+__version__+'\n  Latest update: '+last_update+'\n  Author: '+author+'\n  License: GNU General Public v3 (GPLv3)\n')

def override(func):
    class OverrideAction(argparse.Action):
        def __call__(self,parser,namespace,values,option_string=None):
            func()
            parser.exit()
    return OverrideAction

def check_seq(filename,type,required,strict,limit):
    if filename[-3:]=='.gz':
        f=gzip.open(filename,'rt')
    else:
        f=open(filename,'r')
    t=True
    req=False
    count=0
    new=''
    for line in f:
        if limit and count==limit+1:
            break
        if type==aa:
            l=line.upper().strip()
        else:
            l=line.lower().strip()
        if l and l[0] in ('>','@'):
            count+=1
            new=l[0]
            continue
        if not new:
            continue
        if new=='@':
            new=''
        for i in l:
            if i not in type and not i.isdigit() and i!=' ':
                t=False
                break
            if i in required:
                req=True
        if t==False:
            if strict:
                break
            f.close()
            return False
    else:
        f.close()
        if req==True:
            return True
        if not strict and count>0:
            return False
        if count==0:
            print("\n  File "+filename+" does not contain any fasta or fastq sequence!\n")
            sys.exit()
    f.close()
    if limit and count==limit+1:
        return True
    if t==False:
        print("\n  File "+filename+" contains invalid characters!\n")
    elif req==False:
        print("\n  File "+filename+" does not contain any '"+required+"' nucleotide!\n")
    sys.exit()

def readseq(filename):
    f=open(filename,'r')
    seq=''
    for line in f:
        if line and line[0]=='>':
            seq=''
            continue
        l=line.lower().strip()
        l=''.join(x for x in l if not x.isdigit() and x!=' ')
        seq+=l
    f.close()
    return seq

def readinit(prog):
    lt='undefined'
    pp=''
    lib_nt=''
    number=1
    vrlist=[]
    links=[]
    B=''
    if dbl.check_file('caplib3.conf',False):
        with open('caplib3.conf','r') as f:
            for line in f:
                if line[:14]=='# Library type':
                    B='lt'
                    continue
                if line[:20]=='# Library nucleotide':
                    B='ln'
                    continue
                if line[:16]=='# Parent protein':
                    B='pp'
                    continue
                if line[:11]=='# Numbering':
                    B='number'
                    continue
                if line[:10]=='# Variable':
                    B='vrlist'
                    continue
                elif line[:4]=='# VR':
                    B='links'
                    continue
                if B=='lt':
                    B=''
                    lt=line.lower().strip()
                if B=='pp':
                    B=''
                    pp=line.strip()
                if B=='ln':
                    B=''
                    lib_nt=line.strip()
                elif B=='number':
                    B=''
                    ln=line.strip()
                    if not ln:
                        continue
                    if not ln.isdigit():
                        print('\n  Error in caplib3.conf file: the entry below "# Numbering" must be a number !\n')
                        sys.exit()
                    number=int(ln)
                elif B=='vrlist':
                    if not '\t' in line:
                        B=''
                        continue
                    n=line.strip().split('\t')
                    n=[x for x in n if x]
                    n[1]=int(n[1])
                    vrlist.append(n)
                elif B=='links':
                    if not '\t' in line:
                        B=''
                        continue
                    n=line.strip().split('\t')
                    n=[x for x in n if x]
                    n[2]=int(n[2])
                    n[3]=n[3][1:-1].replace(' ','').split(',')
                    if len(n)==5:
                        n[4]=n[4][1:-1].replace(' ','').split(',')
                    links.append(n)
    if vrlist:
        lt='defined'
    temp=set(x[0] for x in vrlist)
    if len(temp)!=len(vrlist):
        print('\n  Each variable region must have a distinct name!\n')
        sys.exit()
    for n in temp:
        if '-' in n:
            print('\n  Variable regions must not have "-" in their name!\n')
            sys.exit()
    if prog=='link':
        return vrlist
    if prog=='extract':
        temp=set(x[1] for x in links)
        if len(temp)!=len(links):
            print('\n  All prefixes must be different!\n')
            sys.exit()
        return vrlist,links,number,pp,lt
    if prog=='compl':
        return lib_nt,pp,number,vrlist

def detect(l,vrlist,temp):
    a=0
    for i in range(len(vrlist)):
        if i==0:
            n=l.find(vrlist[i][2])
            prevind=0
        else:
            prevind=vrlist[i-1][1]
        n=l[a:min(len(l),round((a+vrlist[i][1]-prevind+len(vrlist[i][3]))*1.15))].find(vrlist[i][2])
        if n==-1:
            continue
        a=a+n+len(vrlist[i][2])
        if i==len(vrlist)-1:
            b=l[a:].rfind(vrlist[i][4])
        else:
            b=l[a:min(len(l),round((a+vrlist[i+1][1]-vrlist[i][1]+len(vrlist[i][3]))*1.15))].rfind(vrlist[i][4])
        if b!=-1:
            a+=b
            temp[i]+=1
    return temp

def findvr(l,vrs,vrdic,vrcnt):
    m=[]
    a=0
    N=False
    for i in range(len(vrs)):
        lp=vrdic[vrs[i]][1]
        rp=vrdic[vrs[i]][3]
        vr=vrdic[vrs[i]][2]
        X=[k.start()+len(lp) for k in regex.finditer(lp,l[a:],overlapped=True)]
        if X:
            b=a+X[0]
            Y=[k.start() for k in regex.finditer(rp,l[b:],overlapped=True)]
            if Y:
                A=[]
                for x in X:
                    for y in Y:
                        if b+y<a+x:
                            continue
                        A.append((a+x,b+y))
                if len(A)>1:
                    z=min([abs(y-x-len(vr)) for (x,y) in A])
                    A=[(x,y) for (x,y) in A if abs(y-x-len(vr))==z]
                if len(A)>1:
                    A=[(x,y) for (x,y) in A if (y-x)%3==0]
                if len(A)>1:
                    A=[(x,y) for (x,y) in A if dbl.match(l[x:y],vr)]
                if len(A)==1:
                    x,y=A[0][0],A[0][1]
                    c=l[x:y]
                    a=y
                    if c and len(c)%3==0:
                        z=dbl.transl(c)
                    else:
                        z=''
                    if len(c)%3!=0:
                        d=1
                        vrcnt[i][1]+=1
                    elif '*' in z:
                        d=2
                        vrcnt[i][2]+=1
                    elif dbl.match(c,vr):
                        d=4
                        vrcnt[i][4]+=1
                    else:
                        d=3
                        vrcnt[i][3]+=1
                    if d>2:
                        vrcnt[i][0][len(c)//3]+=1
                else:
                    Y=''
        if not X or not Y:
            c='*'
            d=0
            z=''
        m.append((c,z,d))
    return m,vrcnt

def aa_dist(aaseq,size,vrs,number,vrdic,fname):
    for n in vrdic.values():
        if len(n)==5:
            mutdist={}
        else:
            mutdist=-1
        break
    aadist={}
    total=[]
    for i in range(len(vrs)):
        total.append(0)
        for seq in aaseq[i]:
            if len(seq)!=size[i]:
                continue
            total[-1]+=aaseq[i][seq][0]
            for n in range(len(seq)):
                j=n+vrdic[vrs[i]][0]//3+number
                if not (j,seq[n]) in aadist:
                    aadist[(j,seq[n])]=0
                aadist[(j,seq[n])]+=aaseq[i][seq][0]
                if mutdist!=-1:
                    if j not in mutdist:
                        mutdist[j]=0
                    if seq[n]==vrdic[vrs[i]][4][n]:
                        mutdist[j]+=aaseq[i][seq][0]
    f=open(fname,'w')
    f.write(','+','.join(n for n in aa)+'\n')
    A=sorted(set([x for (x,_) in aadist]))
    x=0
    y=0
    for n in range(len(A)):
        if n==size[x]+y:
            y+=size[x]
            x+=1
        line=str(A[n])
        for m in aa:
            if (A[n],m) in aadist:
                line+=","+str(aadist[(A[n],m)]/total[x])
            else:
                line+=",0"
        f.write(line+"\n")
    f.close()
    if mutdist!=-1:
        g=open(fname.replace('aad.csv','md.csv'),'w')
        g.write('Position,% mutant\n')
        x=0
        y=0
        for n in range(len(mutdist)):
            if n==size[x]+y:
                y+=size[x]
                x+=1
            m=sorted(mutdist)[n]
            g.write(str(m)+','+str((1-mutdist[m]/total[x])*100)+'\n')
        g.close()

def seqdel(seq,probe,end):
    seq2=dbl.compress(seq[:len(probe)*3+end])
    seq2=seq2[:len(probe)]
    if seq2==probe:
        i=0
    else:
        for i in range(1,len(probe)//2):
            if seq2[:-i]==probe[i:]:
                break
        else:
            return seq
    j=0
    for n in probe[i:-1]:
        while n==seq[j]:
            j+=1
    for i in range(end):
        if seq[j+i]!=seq[j]:
            i-=1
            break
    return seq[j+i+1:]

def findprimer(fp,rp,seq,x,y,a,b,q):
    X=''
    Y=''
    for n in list(fp.keys())+list(rp.keys()):
        if n in fp:
            z=a
        else:
            z=b
        if n[x:]==seq[y:z]:
            X=n
            if n in fp:
                Y='F'
            else:
                Y='R'
            break
    if X:
        mcount[q]+=1
    return (X,Y)

def findsub(fp,rp,seq):
    X=''
    Y=''
    for n in list(fp.keys())+list(rp.keys()):
        y=0
        for i in range(min(len(n),len(seq))):
            if n[i]!=seq[i]:
                y+=1
            if y>1:
                break
        if y==1:
            X=n
            if n in fp:
                Y='F'
            else:
                Y='R'
            break
    if X:
        mcount[3]+=1
    return (X,Y)

def Fseq(x,y,z,sd,fp,rp,ais,s1,s2):
    F=''
    seq=''
    psd=[(k[0],k[1]) for k in sd]
    if x=='F':
        if (fp[y],rp[z]) in psd:
            p=(fp[y],rp[z])
            seq=s1
        else:
            rcount[2]+=1
    else:
        if (fp[z],rp[y]) in psd:
            p=(fp[z],rp[y])
            seq=s2
        else:
            rcount[2]+=1
    if seq:
        s=''
        for n in [k[2:] for k in sd if (k[0],k[1])==p]:
            for m in n:
                if (m[0]=='-' and ais[m[1:]] in seq) or (m[0]=='+' and ais[m[1:]] not in seq):
                    break
            else:
                if s and sd[p+n]!=s:
                    print('\n  Sequence matches more than one sample definition!\n  '+s+', '+sd[p+n]+'\n  Change sample definitions to remove ambiguity!\n\n')
                    sys.exit()
                s=sd[p+n]
        if s:
            F=s
            if T:
                for i in (0,1):
                    c=[k for k,v in (fp,rp)[i].items() if v==p[i]][0]
                    cp=dbl.compress(primers[p[i]]).replace(dbl.compress(c),'')
                    if len(cp)<5:
                        cp=dbl.compress(primers[p[i]])
                    j=len(primers[p[i]])*2
                    if i==0:
                        s1=seq
                    else:
                        s1=dbl.revcomp(seq)
                    if cp in dbl.compress(s1[:j]):
                        while True:
                            if cp not in dbl.compress(s1[:j]):
                                break
                            j-=1
                        b=j+1
                    else:
                        b=len(primers[p[i]])
                    j=0
                    while True:
                        j+=1
                        if primers[p[i]][-j]!=primers[p[i]][-j-1]:
                            break
                    for k in range(j):
                        if s1[b]!=s1[b+k]:
                            break
                    b+=k
                    if T=='P':
                        x=b
                    elif T>0:
                        x=b-len(primers[p[i]])+T
                    elif T<0:
                        x=b+T
                    if i==0:
                        seq=seq[x:]
                    else:
                        seq=seq[:-x]
        else:
            rcount[2]+=1
    return F,seq

def wcomp1(x,y,f):
    if len(x)==0 or len(y)==0:
        return
    parent=defaultdict(list)
    child=defaultdict(list)
    vrs=[]
    if len(x)==1 and 'design' in x[0]:
        a=x[0][:-8]+'\t'
        for n in range(len(vrlist)):
            a+=vrlist[n][0]
            vrs.append(vrlist[n][0])
            if n<len(vrlist)-1:
                a+=','
        parent[0]=[a]
    else:
        j=0
        for n in x:
            b=n[:-16]
            a=b+'\t'
            for i in range(len(links)):
                if links[i][1]==b:
                    a+=','.join(links[i][-1])
                    break
            else:
                continue
            for m in links[i][-1]:
                if m in vrs:
                    j+=1
                    vrs=[]
                vrs.append(m)
            parent[j].append(a)
    j=0
    vrs=[]
    for n in y:
        b=n[:-16]
        a=b+'\t'
        for i in range(len(links)):
            if links[i][1]==b:
                a+=','.join(links[i][-1])
                break
        else:
            continue
        for m in links[i][-1]:
            if m in vrs:
                j+=1
                vrs=[]
            vrs.append(m)
        child[j].append(a)
    if not parent or not child:
        return
    if parent[0][0][parent[0][0].find('\t')-1].isdigit():
        for n in child:
            x=child[n][0][:child[n][0].find('\t')-2]
            y=[parent[k] for k in parent if x in parent[k][0]]
            if len(y)!=1:
                continue
            f.write('\n# Parent group\n')
            for m in y[0]:
                f.write('  '+m+'\n')
            f.write('# Child group\n')
            for m in child[n]:
                f.write('  '+m+'\n')
    else:
        for i in range(len(child)):
            f.write('\n# Parent group\n')
            if len(parent)==1 and len(parent[0])==1:
                a=0
            else:
                a=i
            if a not in parent:
                break
            for n in parent[a]:
                f.write('  '+n+'\n')
            f.write('# Child group\n')
            for n in child[i]:
                f.write('  '+n+'\n')

def get_filtered(x):
    b={}
    cr=glob('*clean_report.txt')
    for crf in cr:
        vr=''
        i=-1
        f=open(crf,'r')
        for line in f:
            ln=line.strip()
            if ln[:16]=='Processing file:' and x in ln:
                vr=ln[ln.find(x)+len(x)+1:ln.find('_extracted')]
                b[vr]=[]
                i=0
            elif vr and i>=0:
                i+=1
                if i in (3,4,11):
                    n=ln[ln.find(':')+2:]
                    if ' ' in n:
                        n=n[:n.find(' ')]
                    b[vr].append(n)
                if i==6 and '-' in vr:
                    i+=2
                    b[vr].append('-')
                if i in (7,8,9):
                    z=ln[ln.find(':')+2:]
                    z=z[:z.find(' ')]
                    if ',' in z:
                        z=z[:z.rfind(',')]
                    if z[:3]=='ost':
                        y=b[vr][-1].split(' ')[1][1:-1]
                    else:
                        y=ln[ln.rfind(', ')+2:ln.find('%')]
                    if i==9:
                        z=str(100-float(y))
                    else:
                        z+=' ('+y+')'
                    b[vr].append(z.replace(',','-'))
                if i==11:
                    i=-1
        f.close()
        if b:
            break
    return b

def enrichment(data1,data2,data3,title1,title2,label,yticklabel,f):
    colors=plt.get_cmap('tab20')
    xticks=[n/10 for n in range(0,10,2)]
    xlabels=[str(i)+'%' for i in range(0,100,20)]
    yticks=[n for n in reversed(range(len(yticklabel)))]
    fig=plt.figure(figsize=(12,6.75))
    plt.subplot(1,3,1)
    plt.title(title1,size=min(13,435/len(title1)),weight='roman')
    left=len(yticklabel)*[0]
    for i in range(len(label)):
        plt.barh([x for x in reversed(range(len(data1)))],[n[i] for n in data1],left=left,color=colors.colors[i])
        left=[left[n]+data1[n][i] for n in range(len(data1))]
    plt.ylim(-0.5,len(data1)-0.5)
    ax=plt.gca()
    ax.tick_params(axis='x',labelsize=8)
    ax.tick_params(axis='y',labelsize=min(8,270/len(yticklabel)))
    plt.xticks(xticks,xlabels)
    plt.yticks(yticks,yticklabel)
    plt.subplot(1,3,2)
    plt.title(title2,size=min(13,435/len(title2)),weight='roman')
    left=len(yticklabel)*[0]
    for i in range(len(label)):
        plt.barh([x for x in reversed(range(len(data2)))],[n[i] for n in data2],left=left,color=colors.colors[i])
        left=[left[n]+data2[n][i] for n in range(len(data2))]
    plt.ylim(-0.5,len(data2)-0.5)
    plt.legend(label,bbox_to_anchor=(2.06,0.3), loc='center left',fontsize=8)
    ax=plt.gca()
    ax.tick_params(axis='x',labelsize=8)
    plt.xticks([n/10 for n in range(0,11,2)],[str(i)+'%' for i in range(0,120,20)])
    ax.axes.get_yaxis().set_visible(False)
    plt.subplot(1,3,3)
    plt.title("Enrichment",size=13,weight='roman')
    ax=plt.gca()
    plt.imshow(data3,aspect='auto',cmap='RdBu')
    cbaxes=fig.add_axes([0.94, 0.6, 0.015, 0.31])
    bar=plt.colorbar(cax=cbaxes)
    bar.ax.tick_params(labelsize=8)
    plt.clim(-1, 1)
    ax.set_xticks(range(len(label)))
    ax.set_xticklabels(label)
    ax.tick_params(axis='x',labelsize=8)
    ax.axes.get_yaxis().set_visible(False)
    plt.subplots_adjust(left=0.06, right=0.93, top=0.91, bottom=0.09,wspace=0.04)
    if isinstance(f,str):
        plt.savefig(f,dpi=600)
        print('  Figure was saved into file: '+f+'\n')
    else:
        f.savefig()
    plt.close()

def main():
    parser=argparse.ArgumentParser(description="NGS analysis of protein combinatorial libraries. For full documentation, visit: https://caplib3.readthedocs.io")
    parser.add_argument('-v','--version',nargs=0,action=override(version),help="Display version")
    subparser=parser.add_subparsers(dest='command',required=True)
    parser_a=subparser.add_parser('demux',help="Demultiplex based on primer sequences")
    parser_a.add_argument('-d','--demux_file',type=str,default='*demux.conf',help="File containing the primer sequences and sample definitions, wildcards accepted (default: single *demux.conf file in the current directory")
    parser_a.add_argument('-r','--read_file',type=str,default='auto',help="File containing the sequencing reads, format: fasta, fastq or gzipped fastq, using wildcards. Always use quotes when using wildcards or path (ex. '*.fq.gz' or 'directory/*.fastq'). Note that only a single file will be selected. Default: autodetect.")
    parser_a.add_argument('-n','--new',default=False,action='store_true',help="Create new caplib3_demux.txt file and rename existing file")
    parser_a.add_argument('-f','--force',default=False,action='store_true',help="Force demutiplexing using current configuration instead of splitting in groups using similar primers.")
    parser_b=subparser.add_parser('init',help="Detect variable regions")
    parser_b.add_argument('-l','--lib_file',type=str,default="",help="File containing the library nucleotide sequence")
    parser_b.add_argument('-m','--min_probe_size',type=int,default=9,help="Minimum size (actual size will vary) in nt of probe used to locate variable regions (default: 9)")
    parser_b.add_argument('-d','--distance',type=int,default=18,help="Minimum distance in nt between variable regions (default: 18, will be adjusted to be compatible with min_probe_size")
    parser_b.add_argument('-f','--frame',type=int,choices=(0,1,2),help="Set reading frame (default: auto-detect)")
    parser_b.add_argument('-p','--parent',type=str,default="",help="Parental nucleotide sequence file name (default: no parent)")
    parser_b.add_argument('-c','--complexity',default=False,action='store_true',help="Redo complexity analysis after modifying the caplib3.conf file manually (default: full initialization, which erases all manual modifications)")
    parser_c=subparser.add_parser('link',help="Match read files to variable regions")
    parser_c.add_argument('-r','--read_files',type=str,default='auto',help="File(s) containing the sequencing reads (after merging paired ends and quality filtering), format: fasta, fastq or gzipped fastq, using wildcards. Always use quotes when using wildcards or path (ex. '*.fq.gz' or 'directory/sample?.fastq'). Note that only files with accepted format will be selected. Default: auto-detect.")
    parser_c.add_argument('-s','--sample_size',type=int,default=100,help="Number of reads used to determine likely variable regions (default: 100)")
    parser_d=subparser.add_parser('extract',help="Extract variable regions from read files")
    parser_e=subparser.add_parser('extract2',help="Extract full sequences from read files and assign fragments to parental sequences")
    parser_e.add_argument('-f','--forward_primer',type=str,default='',help="Forward primer sequence (5' end can be shortened). Optional but recommended for accurate matching, primer sequence will be trimmed to frame.")
    parser_e.add_argument('-r','--reverse_primer',type=str,default='',help="Reverse primer sequence (5' end can be shortened). Optional but recommended for accurate matching, primer sequence will be trimmed to frame.")
    parser_e.add_argument('-p','--parents',type=str,default='',help="File containing the parental sequences in fasta format (partial name OK if no ambiguity)")
    parser_e.add_argument('-s','--sequencing_reads',type=str,default='auto',help="File(s) containing the sequencing reads (partial name OK), format: fasta, fastq or gzipped fastq, using wildcards. Always use quotes when using wildcards or path (ex. '*.fq.gz' or 'directory/sample?.fastq'). Default: all files of accepted format in current directory (except parental sequences).")
    parser_e.add_argument('-d','--detect_strand',default=False,action='store_true',help="Detect correct strand for each read. Default: process direct strand only.")
    parser_e.add_argument('-m','--min_match',type=int,default=10,help="Minimum matching fragment size (default: 10)")
    parser_e.add_argument('-e','--error_correction',type=str,default='fas',help="Sequencing error correction: f=frameshifts, a=ambiguous, s=stop. Correction will be performed only when flanked by parental sequences. Correction is enabled by default for all 3 categories ('fas').")
    parser_e.add_argument('-c','--crude_extract',type=int,default=0,help="Crude extraction to show rough parental composition, with number indicating granularity level (grain size in nt, recommended between 10 and 100). Default: 0 (disabled).")
    parser_f=subparser.add_parser('clean',help="Clean data")
    parser_f.add_argument('-i','--input_files',type=str,default='auto',help="File(s) containing the extracted sequences (created by caplib3 extract), file prefix (partial name) and wildcards accepted (default: all *_extracted.txt files in the current directory")
    parser_f.add_argument('-p','--parents',type=str,default='auto',help="File containing parental aa sequences in fasta format (default: existing *aa.f*a file)")
    parser_f.add_argument('-l','--length',type=str,default='0.1,0.5,0,-1',help="Length filtering options: 4 numbers separated by a comma and surrounded by quotes. Min length frequency in %%, min %% of most common length frequency, min length in aa, max length in aa. Default: '0.1,0.5,0,-1' (-1: no maximum)")
    parser_f.add_argument('-f','--sequence_frequency',type=str,default='0',help="Minimum sequence frequency, either in %% (add the %% sign after the number) or in sequence copy number (integer with no %% sign). Default: 0.")
    parser_f.add_argument('-a','--aa_frequency',type=float,default=0.15,help="Minimum aa frequency in %% at defined variable positions. Default: 0.15. Only valid if defined variable positions exist.")
    parser_f.add_argument('-u','--unmatched_reads',type=float,default=0.001,help="Minimum sequence frequency in %% for reads not perfectly matching library sequence (valid for libraries withh defined variable positions only). Default: 0.")
    parser_f.add_argument('-m','--mutations',type=int,default=-1,help="Maximum number of non-parental positions (valid for undefined libraries only, -1: disabled). Default: -1.")
    parser_f.add_argument('-s','--segments',type=int,default=-1,help="Maximum number of non-parental segments (valid for undefined libraries only, -1: disabled). Default: -1.")
    parser_f.add_argument('-r','--remove_parent',default=False,action='store_true',help="Remove parental sequences")
    parser_g=subparser.add_parser('mix',help="Create amino acid distribution and mutant distribution files of mixed libraries (when sequencing data only exists for individual libraries but not for their mix)")
    parser_g.add_argument('-n','--new',default=False,action='store_true',help="Create new caplib3_mix.txt file and rename existing file")
    parser_h=subparser.add_parser('compare',help="Compare data using tables and plots")
    parser_h.add_argument('-i','--input_files',type=str,default='auto',help="Files containing the data to be compared, wildcards accepted, default: all *report.txt and all *.csv files in the current directory")
    parser_h.add_argument('-f','--file_format',type=str,default='Single multipage pdf',help="Save each figure in separate file with choice of format instead of the default single multipage pdf file. Choices: svg, png, jpg, pdf, ps, eps, pgf, raw, rgba, tif")
    parser_h.add_argument('-n','--new',default=False,action='store_true',help="Create new caplib3_compare.txt and compare_table.csv files and rename existing files")
    parser_i=subparser.add_parser('select',help="Select most enriched variants")
    parser_i.add_argument('-s','--select_file',type=str,help="Configuration file to be used by the select program (bypass the default file caplib3_select.txt)")
    parser_i.add_argument('-f','--file_format',type=str,default='Single multipage pdf',help="Save each figure in separate file with choice of format instead of the default single multipage pdf file. Choices: svg, png, jpg, pdf, ps, eps, pgf, raw, rgba, tif")
    parser_i.add_argument('-n','--new',default=False,action='store_true',help="Create new caplib3_select.txt file and rename existing file")
    parser_j=subparser.add_parser('aa2nt',help="identify original nucleotide sequences encoding a list of selected amino acid sequences")
    parser_j.add_argument('-l','--list',type=str,help="Name or prefix of the file containing the input protein sequences (can be a file created by caplib3 compare or caplib3 select)")
    parser_j.add_argument('-r','--reads',type=str,help="Name or prefix of file containing the nucleotide sequences")
    parser_j.add_argument('-w','--wildtype',type=str,help="Name or prefix of file containing the wild type or reference amino acid sequence (optional, only if the list is an alignment and if it can not be detected automatically)")
    parser_j.add_argument('-m','--min_freq',type=int,default=1,help="Minimum %% (number of reads representing the nt sequence / number of rads representing the target *100) for sequence to be saved (default: 1)")
    args=parser.parse_args()
    if args.command=='demux':
        demux(args)
    if args.command=='init':
        init(args)
    elif args.command=='link':
        link(args)
    elif args.command=='extract':
        extract()
    elif args.command=='clean':
        clean(args)
    elif args.command=='extract2':
        extract2(args)
    elif args.command=='mix':
        mix(args)
    elif args.command=='compare':
        compare(args)
    elif args.command=='select':
        select(args)
    elif args.command=='aa2nt':
        aa2nt(args)

def aa2nt(args):
    if not args.list or not args.reads:
        print('\n  Arguments list and reads are required!\n')
        sys.exit()
    fail=''
    print('\n  Checking list file... ',end='')
    x=glob(args.list+'*')
    if not x:
        fail+='\n  List file not found!'
    if len(x)>1:
        if args.list[:6]=='select':
            x=glob(args.list+'*'+'sequences.txt')
        else:
            x=glob(args.list+'*'+'selected_sequences.txt')
    if len(x)>1:
        fail+='\n  More than one file found! Make the list argument less ambiguous !'
    if args.min_freq<0 or args.min_freq>100:
        fail+='\n  Minimum frequency must be an integer between 0 and 100!'
    if fail:
        print('\n'+fail+'\n')
        sys.exit()
    x=x[0]
    wt=''
    lst,fail=dbl.getfasta(x,dbl.aa,dbl.aa,True)
    if fail and not 'fasta' in fail:
        print('\n'+fail+'\n')
        sys.exit()
    if fail:
        lst,fail,wt=dbl.aln2seq(x,dbl.aa,False,'')
        if fail:
            print('\n'+fail+'\n')
            sys.exit()
    if wt:
        x=glob(wt+'*')
        if len(x)>1:
            x=[k for k in x if not dbl.getfasta(k,dbl.aa,dbl.aa,False)[1] and dbl.getfasta(k,'atgc','atgc',False)[1]]
        if len(x)!=1 and args.wildtype:
            x=glob(args.wildtype+'*')
            if len(x)>1:
                x=[k for k in x if not dbl.getfasta(k,dbl.aa,dbl.aa,False)[1] and dbl.getfasta(k,'atgc','atgc',False)[1]]
        if len(x)==1:
            wt=x[0]
        else:
            print('\n\n  Wild type or reference sequence amino acid file could not be found unambiguously! Run again with the -w argument!\n')
            sys.exit()
    print('OK\n\n  Checking read files...    ',end='')
    z=args.reads
    cl3=''
    fail=''
    seqs=defaultdict(int)
    if '.fa' in x or '.fq' in x:
        z=z[:z.find('.f')]
    x=glob(z+'*')
    if not x:
        fail+='\n  Read file not found!'
    if len(x)>1:
        y=glob(z+'*.cl3')
        if len(y)==1:
            cl3=y[0]
        else:
            x=glob(z+'*.f*')
    if len(x)>1 and not cl3:
        fail+='\n  More than one file found! Make the reads argument less ambiguous !'
    if len(x)==1:
        x=x[0]
        if x.endswith('.cl3'):
            cl3=x
    if x and not cl3:
        fail+=dbl.check_read_file(x)
        nr,fail=dbl.readcount(x,fail)
        if fail:
            print('Problems found!\n'+fail+'\n')
            sys.exit()
        print('OK\n\n  Read file: '+x+'\n  Number of reads: '+str(nr)+'\n')
        f,y,c=dbl.initreadfile(x)
        t='Processing reads...'
        show=dbl.progress_start(nr,t)
        while True:
            l,f,c,_=dbl.getread(f,y,c)
            if not l:
                break
            dbl.progress_check(c,show,t)
            seqs[l]+=1
        dbl.progress_end()
        f.close()
        x=x[:x.find('.')]+'.cl3'
        f=open(x,'w')
        f.write(str(nr)+'\n')
        for n in sorted(seqs,key=seqs.get,reverse=True):
            f.write(n+'\t'+str(seqs[n])+'\n')
        f.close()
        print('  '+str(len(seqs))+' distinct sequences and their copy numbers were saved into file: '+x+'\n')
    if fail:
        print('Problems found!\n'+fail+'\n')
        sys.exit()
    if cl3:
        print('OK\n')
        f=open(cl3,'r')
        nr=f.readline().strip()
        while not nr:
            nr=f.readline().strip()
        if not nr.isdigit():
            print('  Wrong file format for '+cl3+'! Delete the file and run again!\n')
            sys.exit()
        nr=int(nr)
        while True:
            l=f.readline().strip().split()
            if not l:
                break
            seqs[l[0]]=int(l[1])
        f.close()
    rslt={k:defaultdict(int) for k in lst}
    for n in seqs:
        for i in range(3):
            b=n[i:]
            t=dbl.transl(b)
            for m in lst:
                j=0
                for k in lst[m].split(','):
                    a=t.find(k,j)
                    if a==-1:
                        break
                    j=a+len(k)
                else:
                    break
            else:
                continue
            break
        else:
            r=dbl.revcomp(n)
            for i in range(3):
                b=r[:len(r)-i]
                t=dbl.transl(b)
                for m in lst:
                    j=0
                    for k in lst[m].split(','):
                        a=t.find(k,j)
                        if a==-1:
                            break
                        j=a+len(k)
                    else:
                        break
                else:
                    continue
                break
            else:
                continue
        a=t.find(lst[m].split(',')[0])
        if '*' in t[:a]:
            x=t[:a].find('M',t.find('*'))
            if x==-1:
                continue
            b=b[x*3:]
        x=t.find('*',j)
        if x>-1:
            b=b[:(len(t)-x)*3]
        rslt[m][b]+=seqs[n]
    fname=args.list+'--'+args.reads
    for n in ('.txt','.fasta','.fastq','.fa','.fq','.gz'):
        fname=fname.replace(n,'')
    f=open(fname+'_report.txt','w')
    g=open(fname+'_nt.fa','w')
    h=open(fname+'_aa.fa','w')
    for n in rslt:
        dbl.pr2(f,'\n  Target: '+n+'\n'+'  Sequence'.ljust(len(n)+10)+'Reads    %')
        i=0
        nr=sum(rslt[n].values())
        for m in sorted(rslt[n],key=rslt[n].get,reverse=True):
            if rslt[n][m]/nr*100<args.min_freq:
                break
            i+=1
            sn=n+'-'+str(i)
            dbl.pr2(f,'  '+sn.ljust(len(n)+8)+str(rslt[n][m]).rjust(5)+str(round(rslt[n][m]/nr*100,2)).rjust(7))
            g.write('>'+sn+'\n'+m+'\n')
            h.write('>'+sn+'\n'+dbl.transl(m)+'\n')


            # write alignment here (pr2(f,...))


    f.close()
    g.close()
    h.close()
    print('\n  Report was saved into file: '+fname+'_report.txt')
    print('\n  Nucleotide sequences were saved into file: '+fname+'_nt.fa')
    print('\n  Amino acid sequences were saved into file: '+fname+'_aa.fa')
    

#  case input=fasta and extra sequences upstream and downstream -> need to show them
#  NB: wt is file name of aa wt seq! 


def seq2aln(seqs,ref,pos):
    aln=''
    fail=''
    if not seqs or not ref:
        fail+='\n  Sequences or reference missing!'
    if not isinstance(seqs,dict):
        fail+='\n  Sequences must be in dictionary format!'
    if not pos:
        pos=1
    if isinstance(pos,int):
        pos=(pos,)
    elif pos.isdigit():
        pos=(int(pos),)
    elif isinstance(pos,str):
        pos=pos.split(',')
    if isinstance(pos,list):
        for i in range(len(pos)):
            if pos[i].isdigit():
                pos[i]==int(i)
    t='\n  Position must a number or a list of numbers!'
    if isinstance(pos,(list,tuple)):
        for n in pos:
            if not isinstance(n,int):
                fail+=t
                break
    else:
        fail+=t
    if isinstance(ref,str):
        ref=ref.split(',')
    if not isinstance(ref,(list,tuple)):
        fail+='\n  Reference must be a string or a list!'
    if len(ref!=len(pos)):
        fail+='\n  Reference and position must have the same number of items!'
    for n in seqs:
        if isinsitance(seqs[n],str):
            seqs[n]=sqs[n].split(',')
    for n in seqs:
        if not isinsitance(seqs[n],(list,tuple)) or len(seqs[n])!=len(ref):
            fail+='\n  Sequences must be either strings or lists, and each sequence must have the same number of items as the reference!'
            break
    if fail:
        return aln,fail

    




   #  More than 1 segment -> create align directly (only of all seqs have segments of correct size)
                      #  -> if not correct size in any seq in seqs -> must align the region first  

    # single segment -> 
        # if not single size -> align first (add gaps wherever needed)
        # detect variable regions (add optional argument to control of VRs are defined)
        # create align

#  Alignment: Needleman-Wunsch algorithm ! do separately each seq to ref, note new gaps, then add gaps to all seqs at the end

    


    return aln,fail





def demux(args):
    global mcount,rcount,T,primers
    if args.new:
        rename('caplib3_demux.conf')
    dfile=glob(args.demux_file)
    if args.new or (len(dfile)==0 and len(glob('*demux.conf'))==0):
        with open('caplib3_demux.conf','w') as f:
            f.write('# Forward primers, 1 per line: name and sequence (separated by space or tab)\n\n')
            f.write('# Reverse primers, 1 per line: name and sequence (separated by space or tab)\n\n')
            f.write('# Additional internal sequences, 1 per line: name and sequence (separated by space or tab)\n\n')
            f.write('# Sample definitions, 1 per line: sample name, forward primer name, reverse primer name, optional additional internal sequence names (separated by space or tab) preceded by optional sign ("+" or no sign: must be present, "-": must be absent)\n\n')
            f.write('# Leftover reads: Enter file name into which leftover reads will be saved (.fasta extension will be added automatically to the file name). Leftover reads will not be saved if left empty.\n\n')
            f.write('# Trim reads (both ends), options: P (whole primer sequence), positive integer (number of nt to remove from 5\' end), negative integer (number of nt to keep in each primer)\n\n')
            f.write('# Junk to be discarded: all reads containing any of the following sequences will be discarded. Insert optional name before the sequence, followed by space or tab. Optional 2 numbers (separated by a space or tab) after each sequence restrict searching for the sequence within a particular read region (0: first nt of the F primer). If single number, the read will be searched from that number to the read end.\n\n')
        print('\n  Creating file caplib3_demux.conf.\n  Please edit the file, save it under the name of your choice and run the command again.\n\n')
        sys.exit()
    elif len(dfile)==0:
        print('\n  Demux file not found! \n\n')
        sys.exit()
    if len(dfile)>1:
        print('\n  More than one demux file was found in the current directory. Select the one you wish to use using the -i argument followed by the file name.')
        for n in dfile:
            print('  '+n)
        print('\n')
        sys.exit()
    dfile=dfile[0]
    with open(dfile,'r') as f:
        fp={}
        rp={}
        sd={}
        ais={}
        leftover=''
        T=0
        junk=[]
        x=''
        q=0
        fail=''
        for line in f:
            if line[0]=='#':
                x=line[2]
                continue
            l=line.strip().split()
            if not l:
                continue
            if x=='S' and len(l)>=3:
                for i in range(len(l[3:])):
                    if l[3:][i][0] not in '+-':
                        l[3+i]='+'+l[3:][i]
                if l[1] not in fp.values() or l[2] not in rp.values():
                    fail+='\n  Invalid sample definition: primer pair '+l[1]+','+l[2]+' not found!'
                a=[k[1:] for k in l[3:] if k[1:] not in ais]
                if a:
                    fail+='\n  Invalid sample definition: sequence(s) '+', '.join(a)+' not found!'
                a=tuple(l[1:])
                if a in sd or ''.join(map(str,a)) in ''.join(map(str,sd.keys())) or (sd and ''.join(map(str,sd.keys())) in ''.join(map(str,a))):
                    fail+='\n  Duplicate sample definition found!'
                    break
                sd[a]=l[0]
                continue
            if x in ('F','R','A'):
                a=l[1].lower()
                for n in a:
                    if n not in 'atgc':
                        fail+='\n  Invalid sequence!\n  '+l[0]+'\t'+l[1]
                if l[0] in fp.values() or l[0] in rp.values() or l[0] in ais.values() or a in fp or a in rp or a in ais:
                    failed+='\n  Duplicate sequence found!'
                    break
            if x=='A':
                ais[l[0]]=a
            if x=='F':
                fp[a]=l[0]
            elif x=='R':
                rp[a]=l[0]
            if x=='T':
                if len(l)>1 or (not l[0].replace('-','').isdigit() and l[0] not in 'Pp'):
                    fail+='\n  Invalid trim parameter!'
                if l[0] in 'Pp':
                    T='P'
                else:
                    T=int(l[0])
            if x=='L':
                leftover=l[0].replace('.fasta','')
            if x=='J':
                q+=1
                m=str(q)
                if len(l)>1 and not l[1].isdigit():
                    l[1]=l[1].lower()
                    for n in l[1]:
                        if n not in 'atgc':
                            fail+='\n  '+n+' is not a valid nucleotide!'
                            break
                    else:
                        m=l[0]
                        l=l[1:]
                if len(l)>3 or (1<len(l)<4 and not l[-1].isdigit()) or (len(l)==3 and not l[1].isdigit()):
                    fail+='\n  Each line of the junk section, if not empty, must contain a DNA sequence optionally followed by 1 or 2 numbers!'
                    break
                l[0]=l[0].lower()
                for n in l[0]:
                    if n not in 'atgc':
                        fail+='\n  '+n+' is not a valid nucleotide!'
                        break
                else:
                    a=0
                    b=-1
                    if len(l)>1:
                        a=int(l[1])
                    if len(l)==3:
                        b=int(l[2])
                    junk.append([m,l[0],a,b])
                    continue
                break
    if len(fp)==0 or len(rp)==0 or len(sd)==0:
        fail+='\n  Primers or sample definitions are missing!\n\n'
    if fail:
        print('\n  Invalid demux file!'+fail+'\n')
        sys.exit()
    x=[k[0] for k in sd]+[k[1] for k in sd]
    fp={k:fp[k] for k in fp if fp[k] in x}
    rp={k:rp[k] for k in rp if rp[k] in x}
    l=set([len(x) for x in fp]+[len(x) for x in rp])
    primers={v:k  for k,v in {**fp,**rp}.items()}
    fps=list(fp.keys())+list(rp.keys())
    if len(l)>1:
        for n in (fp,rp):
            A=list(n.keys()).copy()
            for i in A:
                if len(i)>min(l) and (i[:min(l)] in fp or i[:min(l)] in rp):
                    print('\n  Primer '+i+" is identical to another primer when 3' trimmed to common length!\n  All primers must be mutually exclusive!\n\n")
                    sys.exit()
                if len(i)!=min(l):
                    n[i[:min(l)]]=n[i]
                    del n[i]
    for i in range(min(10,min(l)),min(l)+1):
        x=[k[:i] for k in (sorted(fp)+sorted(rp))]
        if len(set(x))==len(x):
            break
    for j in range(i,min(l)+1):
        if dbl.diff([k[:j] for k in sorted(fp)+sorted(rp)])>2:
            ec=True
            i=j
            break
    else:
        ec=False
    for j in range(i,min(l)+1):
        x=[k[:j] for k in (sorted(fp)+sorted(rp))]
        y=[dbl.compress(k) for k in x]
        z=min([len(k) for k in y])
        if len(set(y))==len(x) and ((dbl.diff([k[:z] for k in y])>2 and ec) or not ec):
            cmode=True
            i=j
            if dbl.diff([k[:z] for k in y])>2:
                ec=True
            break
    else:
        cmode=False
    if cmode:
        fp={dbl.compress(k[:i]):fp[k] for k in fp}
        rp={dbl.compress(k[:i]):rp[k] for k in rp}
    else:
        fp={k[:i]:fp[k] for k in fp}
        rp={k[:i]:rp[k] for k in rp}
    x='off'
    if ec:
        x='on'
    print('\n  Error correction is '+x)
    x='off'
    if cmode:
        x='on'
    print('\n  Compressed mode is '+x)
    if args.read_file!='auto':
        rfile=glob(args.read_file)
    else:
        rfile=glob('*f*q.gz')
        if not rfile:
            rfile=glob('*.fastq')
        if not rfile:
            rfile=glob('*.fasta')
    if not rfile:
        print("\n  No read file found. Check pattern, or move to correct directory, or include path in pattern.\n\n")
        sys.exit()
    if len(rfile)>1:
        print("\n  More than one file found. Select the correct file using the -r argument followed by the file name.\n  Files found:\n")
        for n in rfile:
            print('  '+n)
        print()
        sys.exit()
    rfile=rfile[0]
    f,y,z,counter=initreadfile(rfile)
    asd=defaultdict(int)
    adseq=defaultdict(int)
    cnt=0
    while cnt<1000:
        l,f,z,counter=getread(f,y,z,counter)
        if not l:
            break
        for n in fps:
            x=l.find(n)
            if x!=-1:
                cnt+=1
                asd[x]+=1
                adseq[l[:x]]+=1
                break
    if counter:
        print('\n  Full primer sequences detected in '+f'{cnt/counter*100:.2f}'+'% of reads\n')
    else:
        print('\n  No read found!\n\n')
        sys.exit()
    if cnt:
        print('  Location of detected primers:')
        print('      Read begins with primer sequence: '+f'{asd[0]/cnt*100:.2f}'+'%')
        print('      1 nt insertion before primer sequence: '+f'{asd[1]/cnt*100:.2f}'+'%')
        x=sum([asd[n] for n in asd if n>1])
        print('      More than 1 nt insertion before primer sequence: '+f'{x/cnt*100:.2f}'+'%')
        x=[n for n in adseq if adseq[n]==max(adseq.values())][0]
        aprobe=''
        if x:
            n=adseq[x]/cnt*100
            L=len(x)*2
            cx=dbl.compress(x)
            counter=0
            count=0
            f.seek(0)
            z=y-2
            while counter<1000:
                l,f,z,counter=getread(f,y,z,counter)
                if not l:
                    break
                counter-=1
                if len(l)<L:
                    continue
                l=dbl.compress(l.lower()[:L])
                l=l[:len(cx)]
                counter+=1
                if cx==l or cx[1:]==l[:-1] or cx[2:]==l[:-2]:
                    count+=1
            ap=count/counter*100
            if ap>50:
                print('\n  Adapter sequence "'+x+'" detected in front of '+f'{n:.2f}'+'% of primer sequences')
                print('  Adapter probe detected in '+f'{ap:.2f}'+'% of reads')
                aprobe=cx
                pend=1
                for i in range(1,len(x)):
                    if x[-i-1]==x[-i]:
                        pend+=1
                    else:
                        break
    else:
        print('\n  No primer sequence detected in reads!\n\n')
        sys.exit()
    f.seek(0)
    z=y-2
    rcount=[0,0,0]
    mcount=[0,0,0,0,0]
    cnt=defaultdict(int)
    jcn=defaultdict(int)
    jc2=defaultdict(int)
    files={n:open(n+'.fasta','w') for n in sd.values()}
    if leftover:
        files[leftover]=open(leftover+'.fasta','w')
    L=i*3
    print('\n  Processing read file, please wait...')
    name2=''
    while True:
        if not y:
            l=''
            while True:
                line=f.readline().strip()
                if not l and line and line[0]=='>':
                    name2=line
                    continue
                if l and (not line or line[0]=='>'):
                    name=name2
                    name2=line
                    break
                l+=line
                if not l:
                    break
        else:
            while z<y:
                l=f.readline().strip()
                if z==y-2:
                    name=l
                z+=1
        if not l:
            break
        l=l.lower()
        if aprobe:
            l=seqdel(l,aprobe,pend)
            lrc=dbl.revcomp(l)
            lrc=seqdel(lrc,aprobe,pend)
            l=dbl.revcomp(lrc)
        else:
            lrc=dbl.revcomp(l)
        z=0
        rcount[0]+=1
        if cmode:
            m=dbl.compress(l[:min(L,len(l))])
            mrc=dbl.compress(lrc[:min(L,len(lrc))])
        else:
            m=l[:min(L,len(l))]
            mrc=lrc[:min(L,len(lrc))]
        a=len(list(fp.keys())[0])
        b=len(list(rp.keys())[0])
        F=''
        S0=findprimer(fp,rp,m,0,0,a,b,0)
        S1=findprimer(fp,rp,mrc,0,0,a,b,0)
        if S0[0] and S1[0] and S0[1]!=S1[1]:
            F,seq=Fseq(S0[1],S0[0],S1[0],sd,fp,rp,ais,l,lrc)
        else:
            Q=False
        if not F and ec:
            if S0[0] and S1[0] and S0[1]=='F':
                Q=True
                T0=findprimer({},rp,m,1,0,a-1,b-1,1)
                T1=findprimer({},rp,mrc,1,0,a-1,b-1,1)
            elif S0[0] and S1[0] and S0[1]=='R':
                Q=True
                T0=findprimer(fp,{},m,1,0,a-1,b-1,1)
                T1=findprimer(fp,{},mrc,1,0,a-1,b-1,1)
            elif S0[0] and not S1[0] and S0[1]=='F':
                S1=findprimer({},rp,mrc,1,0,a-1,b-1,1)
            elif S0[0] and not S1[0] and S0[1]=='R':
                S1=findprimer(fp,{},mrc,1,0,a-1,b-1,1)
            elif not S0[0] and S1[0] and S1[1]=='F':
                S0=findprimer({},rp,m,1,0,a-1,b-1,1)
            elif not S0[0] and S1[0] and S1[1]=='R':
                S0=findprimer(fp,{},m,1,0,a-1,b-1,1)
            elif not S0[0] and not S1[0]:
                S0=findprimer(fp,rp,m,1,0,a-1,b-1,1)
                S1=findprimer(fp,rp,mrc,1,0,a-1,b-1,1)
            if Q and T0[0] and not T1[0]:
                F,seq=Fseq(S1[1],S1[0],T0[0],sd,fp,rp,ais,lrc,l)
            elif Q and T1[0] and not T0[0]:
                F,seq=Fseq(S0[1],S0[0],T1[0],sd,fp,rp,ais,l,lrc)
            elif not Q and S0[0] and S1[0] and S0[1]!=S1[1]:
                F,seq=Fseq(S0[1],S0[0],S1[0],sd,fp,rp,ais,l,lrc)
        if not F and ec:
            if Q and not T0[0] and not T1[0]:
                if S0[1]=='F':
                    T0=findprimer({},rp,m,0,1,a+1,b+1,2)
                    T1=findprimer({},rp,mrc,0,1,a+1,b+1,2)
                else:
                    T0=findprimer(fp,{},m,0,1,a+1,b+1,2)
                    T1=findprimer(fp,{},mrc,0,1,a+1,b+1,2)
            elif S0[0] and not S1[0] and S0[1]=='F':
                S1=findprimer({},rp,mrc,0,1,a+1,b+1,2)
            elif S0[0] and not S1[0] and S0[1]=='R':
                S1=findprimer(fp,{},mrc,0,1,a+1,b+1,2)
            elif not S0[0] and S1[0] and S1[1]=='F':
                S0=findprimer({},rp,m,0,1,a+1,b+1,2)
            elif not S0[0] and S1[0] and S1[1]=='R':
                S0=findprimer(fp,{},m,0,1,a+1,b+1,2)
            elif not S0[0] and not S1[0]:
                S0=findprimer(fp,rp,m,0,1,a+1,b+1,2)
                S1=findprimer(fp,rp,mrc,0,1,a+1,b+1,2)
            if Q and T0[0] and not T1[0]:
                F,seq=Fseq(S1[1],S1[0],T0[0],sd,fp,rp,ais,lrc,l)
            elif Q and T1[0] and not T0[0]:
                F,seq=Fseq(S0[1],S0[0],T1[0],sd,fp,rp,ais,l,lrc)
            elif not Q and S0[0] and S1[0] and S0[1]!=S1[1]:
                F,seq=Fseq(S0[1],S0[0],S1[0],sd,fp,rp,ais,l,lrc)
        if not F and ec:
            if Q and not T0[0] and not T1[0]:
                if S0[1]=='F':
                    T0=findsub({},rp,m)
                    T1=findsub({},rp,mrc)
                else:
                    T0=findsub(fp,{},m)
                    T1=findsub(fp,{},mrc)
            elif S0[0] and not S1[0] and S0[1]=='F':
                S1=findsub({},rp,mrc)
            elif S0[0] and not S1[0] and S0[1]=='R':
                S1=findsub(fp,{},mrc)
            elif not S0[0] and S1[0] and S1[1]=='F':
                S0=findsub({},rp,m)
            elif not S0[0] and S1[0] and S1[1]=='R':
                S0=findsub(fp,{},m)
            elif not S0[0] and not S1[0]:
                S0=findsub(fp,rp,m)
                S1=findsub(fp,rp,mrc)
            if Q and T0[0] and not T1[0]:
                F,seq=Fseq(S1[1],S1[0],T0[0],sd,fp,rp,ais,lrc,l)
            elif Q and T1[0] and not T0[0]:
                F,seq=Fseq(S0[1],S0[0],T1[0],sd,fp,rp,ais,l,lrc)
            elif not Q and S0[0] and S1[0] and S0[1]!=S1[1]:
                F,seq=Fseq(S0[1],S0[0],S1[0],sd,fp,rp,ais,l,lrc)
        if not F:
            T0=[]
            T1=[]
            if S0[0]:
                T0.append(S0)
            if S1[0]:
                T1.append(S1)
            for n in list(fp.keys())+list(rp.keys()):
                if n in m:
                    if n in fp:
                        p='F'
                    else:
                        p='R'
                    if (n,p) not in T0:
                        T0.append((n,p))
                if n in mrc:
                    if n in fp:
                        p='F'
                    else:
                        p='R'
                    if (n,p) not in T1:
                        T1.append((n,p))
            A=[i for i in T0 if i[1]=='F']
            B=[i for i in T0 if i[1]=='R']
            C=[i for i in T1 if i[1]=='F']
            D=[i for i in T1 if i[1]=='R']
            if len(A)==1 and len(B)!=1 or len(B)==1 and len(A)!=1:
                mcount[4]+=1
                if len(A)==1:
                    T0=A[0]
                else:
                    T0=B[0]
            if len(C)==1 and len(D)!=1 or len(D)==1 and len(C)!=1:
                mcount[4]+=1
                if len(C)==1:
                    T1=C[0]
                else:
                    T1=D[0]
            if len(T0)==1 and len(T1)==1 and T0[1]!=T1[1]:
                F,seq=Fseq(T0[1],T0[0],T1[0],sd,fp,rp,ais,l,lrc)
        if not F and not leftover:
            continue
        if not F and leftover:
            seq=l
            F=leftover
            rcount[2]+=1
        else:
            rcount[1]+=1
        for n in junk:
            if n[1] in seq[n[2]:n[3]]:
                jcn[F]+=1
                jc2[n[0]]+=1
                break
        else:
            files[F].write('>'+name[1:]+'\n'+seq+'\n')
            cnt[F]+=1
    for g in files:
        files[g].close()
    f.close()
    a=len(str(rcount[0]))
    print('\n  Processed reads:  '+str(rcount[0]))
    print('  Assigned reads:   '+' '*(a-len(str(rcount[1])))+str(rcount[1]))
    print('  Unassigned reads: '+' '*(a-len(str(rcount[2])))+str(rcount[2])+'\n')
    print('  Primer match counts:')
    a=len(str(max(mcount)))
    print('      Perfect match:              '+' '*(a-len(str(mcount[0])))+str(mcount[0]))
    if ec:
        print('      Match after -1 shift:       '+' '*(a-len(str(mcount[1])))+str(mcount[1]))
        print('      Match after +1 shift:       '+' '*(a-len(str(mcount[2])))+str(mcount[2]))
        print('      Match after 1 substitution: '+' '*(a-len(str(mcount[3])))+str(mcount[3]))
    print('      Other match:                '+' '*(a-len(str(mcount[4])))+str(mcount[4])+'\n')
    print('  File name                      Detected reads              Junk (%)        Saved reads (%)')
    for n in sorted(cnt):
        a=str(cnt[n]+jcn[n])
        b=str(jcn[n])
        c=str(cnt[n])
        d='('+str(round(jcn[n]/(cnt[n]+jcn[n])*100,1))+'%)'
        e='('+str(round(cnt[n]/(cnt[n]+jcn[n])*100,1))+'%)'
        print('  '+n+'.fasta'+' '*(39-len(n)-len(a))+a+' '*(14-len(b))+b+' '*(8-len(d))+d+' '*(15-len(c))+c+' '*(8-len(e))+e)
    if junk:
        print('\n  Junk composition:\n  Name                       Reads      %')
        total=sum(jc2.values())
        for n in sorted(jc2):
            a=str(round(jc2[n]/total*100,1))+'%'
            print('  '+n+' '*(32-len(n)-len(str(jc2[n])))+str(jc2[n])+' '*(7-len(a))+a)
    print()

def init(args):
    if not args.lib_file and args.parent:
        init2(args)
        return
    if args.lib_file and args.complexity:
        print('\n  Arguments lib_file and complexity are mutually exclusive! CHoose one or the other, not both.\n')
        sys.exit()
    def compl1(lib_file,lib_nt,frame,par_aa,number,vrlist):
        if not vrlist:
            lib_file,par_aa_file,number,vrlist=readinit('compl')
            lib_nt=readseq(lib_file)
            par_aa=readseq(par_aa_file).upper()
            frame=vrlist[0][1]%3
            print()
        t=dbl.complexity(lib_nt[frame:])
        fname=lib_file[:lib_file.rfind('.')]
        if fname[-2:]=='nt' and fname[-3] in ('-','_','.'):
            fname=fname[:-3]
        fname=fname[fname.rfind('\\')+1:]
        fname=fname[fname.rfind('/')+1:]
        f=open(fname+'-complexity.txt','w')
        x=len([k for k in t if len(k)>1])
        f.write('COMPLEXITY REPORT\nFile: '+lib_file+'\nReading frame: '+str(frame)+'\nVariable regions: '+str(len(vrlist))+'\nAmbiguous codons: '+str(x)+'\n')
        g=open(fname+'_design_aad.csv','w')
        g.write(','+','.join(n for n in aa)+'\n')
        if par_aa:
            h=open(fname+'_design_md.csv','w')
            h.write('Position,% mutant\n')
        gc=1
        for n in vrlist:
            nac=0
            i=(n[1]-frame)//3
            j=i+len(n[3])//3
            ac=1
            af=1
            sf=1
            for k in range(i,j):
                if len(t[k])==1:
                    continue
                nac+=1
                x=len(t[k])
                y=1
                q=sum(t[k].values())
                if '*' in t[k]:
                    x-=1
                    y=(q-t[k]['*'])/q
                ac*=x
                af*=y
            sf=(1-af)*100
            gc*=ac
            f.write('\nVariable region name: '+n[0]+'\nVariable region sequence: '+n[3]+'\nExpected stop codon frequency: '+f'{sf:.2f}'+'%\nExpected amino acid complexity: '+str(ac)+'\n')
            f.write('Number of ambiguous codons: '+str(nac)+'\nDetailed codon analysis:\nIndex\tPosition\tCodon\tStop %\t#aa\tTranslation\n')
            for k in range(i,j):
                f.write(str(k)+'\t'+str(k+number)+'\t\t'+lib_nt[frame+k*3:frame+3+k*3]+'\t')
                x=len(t[k])
                y=0
                if '*' in t[k]:
                    y=t[k]['*']
                    x-=1
                q=sum(t[k].values())
                f.write(f'{y/q*100:.2f}'+'\t'+str(x)+'\t')
                for x in sorted(t[k]):
                    f.write(x+':'+str(t[k][x])+' ')
                f.write('\n')
                line=str(k+number)
                for m in aa:
                    if m in t[k]:
                        line+=","+str(t[k][m]/(q-y))
                    else:
                        line+=",0"
                g.write(line+"\n")
                if par_aa:
                    if par_aa[k+number-1] not in t[k]:
                        x=1
                    else:
                        x=t[k][par_aa[k+number-1]]
                        x=(q-x-y)/(q-y)
                    h.write(str(k+number)+','+str(x*100)+'\n')
        f.write('\n')
        f.close()
        g.close()
        print('  Complexity report was saved into file: '+fname+'-complexity.txt')
        print('  Theoretical amino acid distribution was saved into file: '+fname+'_design_aad.csv')
        if par_aa:
            print('  Theoretical mutation distribution was saved into file: '+fname+'_design_md.csv')
            h.close()
        print()
        return
    if args.complexity:
        compl1('','','','','','')
        return
    if not args.lib_file:
        print('\n  Argument --lib_file (-l) is required for defined libraries, and argument --parent (-p) is required for undefined libraries!\n')
        sys.exit()
    dbl.check_file(args.lib_file,True)
    check_seq(args.lib_file,'atgc'+ambiguous,ambiguous,True,0)
    if args.parent:
        dbl.check_file(args.parent,True)
        check_seq(args.parent,'atgc','atgc',True,0)
        par_nt=readseq(args.parent)
        temp=[]
        for frame in range(3):
            temp.append(dbl.transl(par_nt[frame:3*(len(par_nt[frame:])//3)+frame]).strip().upper())
        if not '*' in temp[0][:-1]:
            par_aa=temp[0]
        elif not '*' in temp[1][:-1] and '*' in temp[2][:-1]:
            par_aa=temp[1]
        elif not '*' in temp[2][:-1] and '*' in temp[1][:-1]:
            par_aa=temp[2]
        else:
            print('\n  Could not identify reading frame for parent sequence.\n')
            sys.exit()
    if args.min_probe_size>=args.distance:
        args.distance=args.min_probe_size+1
    lib_nt=readseq(args.lib_file)
    if args.frame==None:
        a=0
        b=3
    else:
        a=args.frame
        b=a+1
    temp=[]
    for frame in range(a,b):
        lib_aa=dbl.transl(lib_nt[frame:3*(len(lib_nt[frame:])//3)+frame]).strip()
        if '*' in lib_aa[:-1] and a!=b-1:
            continue
        if not args.parent:
            number=1
            score=0
        else:
            for i in range(len(lib_aa)):
                if lib_aa[i] in ('X','B','J','Z'):
                    break
            while True:
                n=par_aa.find(lib_aa[:i])
                if n!=-1 or i<7:
                    break
                i-=1
            if i<7:
                number=1
                score=0
            elif i>=7 and n!=-1:
                number=n+1
                score=i
        temp.append((frame,lib_aa,score,number))
    if not temp:
        print("  Failed to detect reading frame. Check the library sequence file or use -f argument to force a particular reading frame.\n")
        sys.exit()
    n=max(x[2] for x in temp)
    i=[x[2] for x in temp].count(n)
    if i>1:
        print("  More than one possible reading frame. Use -f argument to set the correct reading frame.\n")
        sys.exit()
    for x in temp:
        if x[2]==n:
            break
    temp=(x)
    frame=temp[0]
    lib_aa=temp[1]
    number=temp[3]
    temp1=args.lib_file[:args.lib_file.rfind('.')]
    if temp1[-2:]=='nt':
        temp1=temp1[:-2]+'aa.fasta'
    else:
        temp1+='-aa.fasta'
    temp1=temp1[temp1.rfind('\\')+1:]
    temp1=temp1[temp1.rfind('/')+1:]
    with open(temp1,'w') as f:
        f.write('>'+temp1[:-6]+'\n'+lib_aa+'\n')
    print('\n  Library protein sequence was saved as '+temp1)
    vrl2=''
    if dbl.check_file('caplib3.conf',False):
        vrl2=[k[0] for k in readinit('link')]
    rename('caplib3.conf')
    ifile=open('caplib3.conf','w')
    ifile.write('# Library type:\ndefined\n\n')
    ifile.write('# Library nucleotide sequence file name:\n'+args.lib_file+'\n\n# Library protein sequence file name:\n'+temp1)
    temp1=''
    if args.parent:
        temp1=args.parent[:args.parent.rfind('.')]
        if temp1[-2:]=='nt':
            temp1=temp1[:-2]+'aa.fasta'
        else:
            temp1+='-aa.fasta'
        temp1=temp1[temp1.rfind('\\')+1:]
        temp1=temp1[temp1.rfind('/')+1:]
        with open(temp1,'w') as f:
            f.write('>'+temp1[:-6]+'\n'+par_aa+'\n')
        print('\n  Parent protein sequence was saved as '+temp1)
    if number>1:
        print('\n  First amino acid position in library sequence corresponds to position '+str(number)+' in parent sequence.')
    ifile.write('\n\n# Parent nucleotide sequence file name:\n'+args.parent+'\n\n'+'# Parent protein sequence file name:\n'+temp1+'\n\n# Numbering (number of first aa position in corresponding parental sequence):\n'+str(number)+'\n')
    vrlist=VR(frame,lib_nt,args)
    vrlist1=''
    if args.parent:
        i=0
        A=''
        lib2=lib_nt
        for n in range(len(vrlist)+1):
            i=int(vrlist[n-1][1])+len(vrlist[n-1][3])
            if n==len(vrlist):
                j=len(lib_nt)
            else:
                j=int(vrlist[n][1])
            if lib_nt[i:j] in par_nt[par_nt.find(A)+len(A):]:
                if n!=len(vrlist):
                    A=lib_nt[i:j]
                    i=int(vrlist[n][1])+len(vrlist[n][3])
                continue
            b=i
            while b<j:
                a=i
                b=a+6
                while b<j and lib_nt[a:b] not in par_nt[par_nt.find(A)+len(A):]:
                    a+=1
                    b+=1
                if a!=i or b==j:
                    if b==j:
                        x=par_nt.find(A)+len(A)
                        p=par_nt[x:x+j-i]
                        l=lib_nt[i:j]
                    else:
                        c=b
                        while c<j and lib_nt[a:c] in par_nt[par_nt.find(A)+len(A):]:
                            c+=1
                        x=par_nt[par_nt.find(A)+len(A):].find(lib_nt[a:c-1])
                        p=par_nt[x-a+i:x]
                        l=lib_nt[i:a]
                    q=''
                    for x in range(len(p)):
                        q+=ambiguous[dbl.IUPAC.index(set((l[x],p[x])))]
                    lib2=lib2[:i]+q+lib2[a:]
                while b<=j and lib_nt[a:b] in par_nt[par_nt.find(A)+len(A):]:
                    b+=1
                i=b-1
                if b==j:
                    A=lib_nt[a:j]
                else:
                    A=lib_nt[a:b-1]
                continue
        if lib2!=lib_nt:
            vrlist1=list(vrlist)
            vrlist=VR(frame,lib2,args)
            print('  Note: parental sequence was found to differ from the library sequence outside designed variable regions. New variable regions were created accordingly. However, only the original design will be used to calculate theoretical complexities.\n')
        if len(vrlist)==len(vrl2):
            for i in range(len(vrlist)):
                vrlist[i][0]=vrl2[i]
        vrdic={}
        for n in vrlist:
            vrdic[n[0]]=n[1:]
        vrcnt=[]
        limit=0
        for i in vrlist:
            limit+=len(i[2])+len(i[3])
            vrcnt.append([])
            vrcnt[-1].append(defaultdict(int))
            for j in range(4):
                vrcnt[-1].append(0)
        pvr,_=findvr(par_nt[number*3:],list(vrdic.keys()),vrdic,vrcnt)
    T='Variable regions (Name, VR index, Left probe sequence, VR sequence, Right probe sequence'
    if args.parent:
        T+=', parent VR aa sequence):'
    else:
        T+='):'
    ifile.write('\n# '+T+'\n')
    print('\n  '+T)
    for i in range(len(vrlist)):
        T=vrlist[i][0]+'\t'+str(vrlist[i][1])+'\t'+vrlist[i][2]+'\t'+vrlist[i][3]+'\t'+vrlist[i][4]
        if args.parent:
            T+='\t'+pvr[i][1]
        ifile.write(T+'\n')
        print(T)
    ifile.close()
    print('\n  In order to make the variable regions larger (fewer regions) or smaller (more regions), adjust the -d argument accordingly.\n')
    print('  Note: Check the caplib3.conf file in the working directory and make changes as necessary before proceeding further.')
    print('  In particular, you may need to correct the parental sequence and numbering, as well as rename the variable regions.')
    print('  Run caplib3.py init -c to reflect VR name changes into the complexity report\n')
    lib_file=args.lib_file
    compl1(lib_file,lib_nt,frame,par_aa,number,vrlist)

def init2(args):
    pass







def VR(frame,lib_nt,args):
    vrlist=[]
    a=0
    vr=''
    z=True
    for n in range(frame,len(lib_nt),3):
        x=lib_nt[n:n+3]
        for i in x:
            if i not in 'atgc':
                break
        else:
            if n==range(frame,len(lib_nt),3)[-1]:
                pass
            elif z:
                continue
            else:
                vr+=lib_nt[a:n]
                a=n
                z=True
                continue
        if not z:
            continue
        if n==range(frame,len(lib_nt),3)[-1]:
            i=min(a+args.min_probe_size,len(lib_nt))
            rprobe=lib_nt[a:i]
            while True:
                if lib_nt.rfind(rprobe,a)==a or i==len(lib_nt):
                    break
                i+=1
                rprobe=lib_nt[a:i]
            vrlist.append([b+len(lprobe),lprobe,vr,rprobe])
        elif n-a<args.distance and a!=0:
            vr+=lib_nt[a:n]
        elif a==0:
            i=max(n-args.min_probe_size,0)
            lprobe=lib_nt[i:n]
            while True:
                if lib_nt.find(lprobe)==i:
                    break
                i-=1
                lprobe=lib_nt[i:n]
            b=i
        elif n-a>=args.distance and a!=0:
            i=a+args.min_probe_size
            rprobe=lib_nt[a:i]
            while True:
                if lib_nt.rfind(rprobe,a)==a:
                    break
                i+=1
                rprobe=lib_nt[a:i]
            vrlist.append([b+len(lprobe),lprobe,vr,rprobe])
            vr=''
            i=n-args.min_probe_size
            lprobe=lib_nt[i:n]
            while True:
                if lib_nt.find(lprobe,a)==i:
                    break
                i-=1
                lprobe=lib_nt[i:n]
            b=i
        a=n
        z=False
    for i in range(len(vrlist)):
        vrlist[i].insert(0,'VR'+str(i+1))
    return vrlist

def link(args):
    print()
    rfiles=findreadfiles(args.read_files,('atgc'+ambiguous,'atgc'),('',))
    vrlist=readinit('link')
    if not vrlist:
        print('  List of variable regions not found in caplib3.conf !\n')
        sys.exit()
    temp={}
    strand={}
    for x in rfiles:
        if x[-3:]=='.gz':
            f=gzip.open(x,'rt')
        else:
            f=open(x,'r')
        l=f.readline().strip()
        if not l or l[0] not in ('>','@'):
            f.close()
            print('  '+x+' does not look like a fastq or fasta file.\n')
            continue
        temp0=[]
        temp1=[]
        for vr in vrlist:
            temp0.append(0)
            temp1.append(0)
        if l[0]=='>':
            seq=2
            z=1
        else:
            seq=4
            z=3
        count=0
        while count<args.sample_size:
            while z<seq:
                l=f.readline().lower().strip()
                z+=1
            if not l:
                break
            lrc=dbl.revcomp(l)
            z=0
            count+=1
            temp0=detect(l,vrlist,temp0)
            temp1=detect(lrc,vrlist,temp1)
        f.close()
        print("\n  File: "+x+", reads tested: "+str(count)+"\n  Orientation: ",end='')
        for n in (temp0,temp1):
            for i in range(len(n)):
                if n[i]/count>0.1:
                    n[i]=1
                else:
                    n[i]=0
        if temp0==temp1 and sum(temp0)>0:
            strand[x]=2
            print("both")
        elif sum(temp0)>sum(temp1):
            strand[x]=0
            print("direct strand")
        elif sum(temp0)<sum(temp1):
            strand[x]=1
            print("reverse complement")
        else:
            temp[x]=[]
            strand[x]=-1
            print('failed to detect!')
            continue
        if strand[x]!=1:
            temp[x]=temp0
        else:
            temp[x]=temp1
        print("  Variable regions detected: ",end='')
        z=False
        for i in range(len(temp[x])):
            if temp[x][i]:
                if z:
                    print(', ',end='')
                print(vrlist[i][0],end='')
                z=True
        if z:
            print()
        else:
            print('none')
    print()
    with open("caplib3.conf", "r") as f:
        x=f.readlines()
    with open("caplib3.conf", "w") as f:
        for l in x:
            if l[:4]=='# VR':
                break
            f.write(l)
        else:
            f.write('\n')
        f.write('# VRs assigned to files (read file, prefix, orientation (0: direct, 1: reverse, 2: both), individual VR, combined VR):\n' )
        for x in sorted(temp):
            a=x[x.find('\\')+1:]
            a=a[a.find('/')+1:]
            z=x+'\t'+a[:a.find('.')]+'\t'+str(strand[x])+'\t['
            temp1=[]
            for i in range(len(temp[x])):
                if temp[x][i]:
                    temp1.append(vrlist[i][0])
            if len(temp1)==0:
                continue
            for i in range(len(temp1)):
                z+=temp1[i]
                if i!=len(temp1)-1:
                    z+=','
            z+=']'
            if len(temp1)>1:
                z+='\t'+z[z.find('['):]
            f.write(z+'\n')
        print('  Variable region assignments to read files were saved into file caplib3.conf')
        print('  Edit the "# VRs assigned..." section in that file to change the prefixes (fist part of name of files that will be created during extraction and analysis).')
        print('  Also change the "combined VR" selections according to your needs (a combined VR will be treated as a single VR, and processed in addition to all the individual VRs).\n')

def extract():
    vrlist,links,number,_,lt=readinit('extract')
    if not vrlist:
        print('  List of variable regions not found in caplib3.conf !\n')
    if not links:
        print('  Variable region assignments not found in caplib3.conf !\n')
    if not vrlist or not links:
        sys.exit()
    vrdic={}
    for n in vrlist:
        vrdic[n[0]]=n[1:]
    for x in links:
        reads=[0,0,0,0]
        vrcnt=[]
        aaseq=[]
        comb=[0,0,0,0,0]
        es=[]
        for i in x[3]:
            vrcnt.append([])
            vrcnt[-1].append(defaultdict(int))
            for j in range(4):
                vrcnt[-1].append(0)
            aaseq.append({})
        if len(x)==5:
            aaseq.append({})
            j=[x[3].index(n) for n in x[3] if n in x[4]]
        if x[0][-3:]=='.gz':
            f=gzip.open(x[0],'rt')
        else:
            f=open(x[0],'r')
        l=f.readline().strip()
        if not l or l[0] not in ('>','@'):
            f.close()
            continue
            print('  '+x+' does not look like a fastq or fasta file.\n')
        print('\n  Processing read file: '+x[0])
        if l[0]=='>':
            y=2
            z=1
        else:
            y=4
            z=3
        while True:
            while z<y:
                l=f.readline().lower().strip()
                z+=1
            if not l:
                break
            z=0
            reads[0]+=1
            if x[2]==0:
                m,vrcnt=findvr(l,x[3],vrdic,vrcnt)
            elif x[2]==1:
                m,vrcnt=findvr(dbl.revcomp(l),x[3],vrdic,vrcnt)
            else:
                m0=findvr(l,x[3],vrdic,vrcnt)
                m1=findvr(dbl.revcomp(l),x[3],vrdic,vrcnt)
                if sum(i for (_,_,i) in m0[0])>sum(i for (_,_,i) in m1[0]):
                    m,vrcnt=m0[0],m0[1]
                elif sum(i for (_,_,i) in m0[0])<sum(i for (_,_,i) in m1[0]):
                    m,vrcnt=m1[0],m1[1]
                else:
                    continue
            a=[i[2] for i in m]
            c3=a.count(3)
            c4=a.count(4)
            if c3+c4>0:
                reads[1]+=1
            if c3+c4==len(m):
                reads[2]+=1
            if c4==len(m):
                reads[3]+=1
            for i in range(len(m)):
                if m[i][2]>2:
                    if m[i][1] not in aaseq[i]:
                        if m[i][2]==4:
                            aaseq[i][m[i][1]]=[0,True]
                        else:
                            aaseq[i][m[i][1]]=[0,False]
                    aaseq[i][m[i][1]][0]+=1
            if len(x)==5:
                m1=[]
                m2=True
                temp=[m[n][2] for n in j]
                if 0 not in temp:
                    comb[0]+=1
                if 0 not in temp and 1 in temp:
                    comb[1]+=1
                if 0 not in temp and 1 not in temp and 2 in temp:
                    comb[2]+=1
                for i in range(len(x[3])):
                    if x[3][i] not in x[4]:
                        continue
                    if m[i][2]<3:
                        m1=[]
                        break
                    m1.append(m[i][1])
                    if m[i][2]==3:
                        m2=False
                else:
                    m1=','.join(m1)
                    comb[3]+=1
                    if m2==True:
                        comb[4]+=1
                    if m1 not in aaseq[-1]:
                        aaseq[-1][m1]=[0,m2]
                    aaseq[-1][m1][0]+=1
        f.close()
        h=open(x[1]+'_extract_report.txt','w')
        h.write('Read file:\n'+x[0]+'\n\nVariable regions (name, sequence):\n')
        for i in range(len(x[3])):
            h.write(x[3][i]+'\t'+vrdic[x[3][i]][2]+'\n')
        for T in ('Processed reads: '+str(reads[0]),'Reads with at least one valid VR: '+str(reads[1]),'Reads with all VRs detected and valid: '+str(reads[2]),'Reads with all VRs perfectly matching the library: '+str(reads[3])):
            print('  '+T)
            h.write('\n'+T)
        for i in range(len(x[3])+1):
            if i==len(x[3]) and len(x)<5:
                continue
            if i==len(x[3]):
                fname=x[1]+'_'+'-'.join(x[4])+'_extracted.txt'
            else:
                fname=x[1]+'_'+x[3][i]+'_extracted.txt'
            f=open(fname,'w')
            if i<len(x[3]):
                total=vrcnt[i][3]+vrcnt[i][4]
            else:
                total=comb[3]
            f.write(str(total)+'\n')
            temp=sorted(aaseq[i].items(), reverse=True, key=lambda k: k[1])
            for n in temp:
                if type(n[0])==str:
                    T=n[0]
                else:
                    T=','.join(n[0])
                f.write(T+'\t'+str(n[1][0])+'\t'+str(n[1][1])+'\n')
            f.close()
            if i<len(x[3]):
                T='Variable region: '+x[3][i]
                matched=str(vrcnt[i][4])
                a=(str(sum(vrcnt[i][1:])),str(vrcnt[i][1]),str(vrcnt[i][2]))
                f=open(x[1]+'_'+x[3][i]+'_extracted_sd.csv','w')
                f.write('Size (aa)')
                for j in sorted(vrcnt[i][0]):
                    f.write(','+str(j))
                f.write('\nNumber')
                for j in sorted(vrcnt[i][0]):
                    f.write(','+str(vrcnt[i][0][j]))
                f.close()
            else:
                T='Combined variable regions '+'-'.join(x[4])
                matched=str(comb[4])
                a=(str(comb[0]),str(comb[1]),str(comb[2]))
            print('\n  '+T)
            h.write('\n\n'+T)
            for T in ('Sequences detected: '+a[0],
                'Sequences with length not multiple of 3: '+a[1],
                'Sequences containing a stop codon (and length multiple of 3): '+a[2],
                'Valid sequences (length multiple of 3 and no stop codon): '+str(total)):
                print('    '+T)
                h.write('\n  '+T)
            if total==0:
                continue
            if i<len(x[3]):
                mcs=int(max(vrcnt[i][0], key=vrcnt[i][0].get))
                es.append(int(len(vrdic[x[3][i]][2])/3))
                for T in ('Size distribution of extracted protein sequences was saved into file: '+x[1]+'_'+x[3][i]+'_extracted_sd.csv',
                    'Most common size: '+str(mcs)+' aa (expected: '+str(es[-1])+' aa), '+f'{(vrcnt[i][0][mcs]/total*100):.2f}'+'% of sequences'):
                    print('    '+T)
                    h.write('\n  '+T)
                if total>1 and len(sorted(vrcnt[i][0].values()))>1:
                    N=int(list(vrcnt[i][0].keys())[list(vrcnt[i][0].values()).index(sorted(vrcnt[i][0].values())[-2])])
                    T='Next most common size: '+str(N)+' aa, '+f'{(vrcnt[i][0][N]/total*100):.2f}'+'% of sequences'
                    print('    '+T)
                    h.write('\n  '+T)
            if total==0:
                T='No sequence could be extracted'
                print('    '+T)
                h.write('\n  '+T)
                continue
            for T in (str(total)+' protein sequences extracted and saved into file: '+fname,
            'Sequences perfectly matching the library: '+matched,
            'Complexity: '+str(len(aaseq[i]))):
                print('    '+T)
                h.write('\n  '+T)
            if len(vrlist[0])==6:
                if i<len(x[3]):
                    M=vrdic[x[3][i]][4]
                else:
                    M=[]
                    for n in x[4]:
                        M.append(vrdic[n][4])
                    M=','.join(M)
                if M in aaseq[i]:
                    n=aaseq[i][M][0]/total*100
                else:
                    n=0
                T='Parent sequence: '+M+', '+f'{n:.2f}'+'% of sequences'
                print('    '+T)
                h.write('\n  '+T)
            T='Most common sequence: '+str(temp[0][0])+', '+f'{(temp[0][1][0]/total*100):.2f}'+'% of sequences'
            print('    '+T)
            h.write('\n  '+T)
            if total>1 and len(temp)>1:
                T='Next most common sequence: '+str(temp[1][0])+', '+f'{(temp[1][1][0]/total*100):.2f}'+'% of sequences'
                print('    '+T)
                h.write('\n  '+T)
        aa_dist(aaseq,es,x[3],number,vrdic,x[1]+'_extracted_aad.csv')
        T='Amino acid distribution of extracted protein sequences of expected size was saved into file: '+x[1]+'_extracted_aad.csv'
        print('\n  '+T)
        h.write('\n\n'+T+'\n')
        if len(vrlist[0])==6:
            T='Mutation distribution of extracted protein sequences of expected size was saved into file: '+x[1]+'_extracted_md.csv'
            print('\n  '+T)
            h.write(T+'\n\n')
        h.close()
        print('  Report saved into file: '+x[1]+'_extract_report.txt\n')

def clean(args):
# Check arguments
    if args.input_files=='auto':
        x='*_extracted.txt'
    else:
        x=args.input_files+'*'
    files=glob(x)
    files=[x for x in files if ('extracted' in x and '.csv' not in x and 'report' not in x)]
    if not files:
        print("\n  Files not found. Check pattern, or move to correct directory, or include path in pattern.\n")
        sys.exit()
    print('\n  Files selected ('+str(len(files))+'):')
    for n in files:
        print('  '+n)
    print('')
    vrlist,links,number,par,lt=readinit('extract')
    if not par:
        if args.parents=='auto':
            x='*aa.f*a'
        else:
            x=args.parents
        par=glob(x)
        if not par:
            par=glob(x[:x.rfind('.')+1]+'*')
        if not par and args.parents!='auto':
            print('\n  Parental sequence file was not found!\n')
            sys.exit()
        if len(par)>1:
            print('\n  More than one possible parental sequence file! Please provide exact file name!\n')
            for n in par:
                print('  '+n)
            print()
            sys.exit()
        par=par[0]
    if par:
        par=dbl.getfasta(par,dbl.aa,dbl.aa,True)
    length=args.length.replace(' ','').split(',')
    bad=False
    if len(length)!=4:
        bad=True
    else:
        for n in length[:-1]:
            if not n.replace('.', '', 1).isdigit():
                bad=True
                break
        else:
            for i in (0,1):
                length[i]=float(length[i])
                if length[i]<0 or length[i]>100:
                    bad=True
                    break
            else:
                if length[2].isdigit() and (length[3].isdigit() or length[3]=='-1'):
                    length[2]=int(length[2])
                    length[3]=int(length[3])
                else:
                    bad=True
    if bad:
        print('\n  Invalid length filtering options. Must be 4 numbers separated by commas, surrounded by quotes. Two first numbers can be any number between 0 and 100, two last numbers must be integers.\n')
        sys.exit()
    bad=False
    freq=args.sequence_frequency
    if (freq[-1]=='%' or '.' in freq) and freq.replace('.', '', 1).replace('%', '', 1).isdigit():
        freq=(float(freq.replace('%','')),0)
        if freq[0]>100:
            bad=True
    elif freq.isdigit():
        freq=(0,int(freq))
    else:
        bad=True
    if bad:
        print('\n  Invalid sequence frequency filtering option. Must be either a % (between 0 and 100) or an integer.\n')
        sys.exit()
    maf=args.aa_frequency
    if maf>100 or maf<0:
        print('\n  Invalid amino acid frequency. Must be a number between 0 and 100.\n')
        sys.exit()
    ur=args.unmatched_reads
    if ur>100 or ur<0:
        print('\n  Invalid unmatched read frequency. Must be a number between 0 and 100.\n')
        sys.exit()
    npp=args.mutations
    nps=args.segments
    if npp<-1 or nps<-1:
        print('\n  Invalid maximum number of non-parental positions or segments. Must be either -1 (disable) or a positive integer.\n')
        sys.exit()
    if len(files)==1:
        report=files[0][:files[0].rfind('_')+1]
    else:
        report='All_'
# Initialize report
    if lt!='undefined' and not vrlist:
        print('  List of variable regions not found in caplib3.conf !\n')
        sys.exit()
    vrdic={}
    for n in vrlist:
        vrdic[n[0]]=n[1:]
    if len(files)>1 and args.input_files!='auto':
        report=''
        for x in links:
            for y in files:
                if x[1] in y:
                    report+=x[1]+'_'
                    break
    report+='clean_report.txt'
    r=open(report,'w')
    r.write('  Data cleaning report\n\n  Files: '+args.input_files+'\n  Length filtering options: '+args.length+'\n  Minimum sequence frequency: ')
    if freq==(0,0):
        x='none'
    elif not freq[0]:
        x=freq[1]+' reads'
    else:
        x=freq[0]+'%'
    r.write(x+'\n  Minimum aa frequency: '+str(maf)+'\n  Minimum unmatched sequence frequency: '+str(ur)+'\n  Maximum number of mutations: '+str(npp)+'\n  Maximum number of non-parenta segments: '+str(nps)+'\n  Remove parental sequences: '+str(args.remove_parent)+'\n')
# Open sequence files
    for fname in files:
        f=open(fname,'r')
        total=f.readline().strip()
        if total.isdigit():
            total=int(total)
        else:
            dbl.pr2(r,'\n  File '+fname+' is not a valid input file !\n')
            continue
        x=f.readline().strip()
        defined=False
        if x[0]!='(':
            defined=True
# Read distribution files
        sdf=[]
        if defined:
            vrs=[]
            b=fname.replace('_','-').rfind('-')
            while len(vrs)<x.count(',')+1:
                a=fname[:b].replace('_','-').rfind('-')
                if a==-1:
                    dbl.pr2(r,'\n  Ignoring file: '+fname+'\n  Reason: could not find variable region names within file name!')
                    break
                n=fname[a+1:b]
                if n in vrdic:
                    vrs.insert(0,n)
                    b=a
            if a==-1:
                continue
            fn=fname[:b]
            for vr in vrs:
                sdf.append([])
                x=fn+'_'+vr+'_extracted_sd.csv'
                if not dbl.check_file(x,False):
                    dbl.pr2(r,'\n  Warning: could not find size distribution file for variable region: '+vr+' of '+fn+'\n  Filtering will be affected!\n')
                    continue
                sdf=sizefilter(x,sdf,length)
            adf=defaultdict(list)
            x=fn+'_extracted_aad.csv'
            if not dbl.check_file(x,False):
                dbl.pr2(r,'\n  Warning: could not find amino acid distribution file for file: '+fname+'\n  Filtering will be affected!\n')
            else:
                s=open(x,'r')
                a=s.readline().strip().split(',')[1:]
                while True:
                    b=s.readline().strip().split(',')
                    if len(b)==1:
                        break
                    for i in range(len(a)):
                        if float(b[1:][i])*100<maf:
                            adf[int(b[0])].append(a[i])
                s.close()
        else:
            x=fname.replace('.txt','_sd.csv')
            sdf.append([])
            sdf=sizefilter(x,sdf,length)[0]
# Process sequences
        filtered=[]
        ftotal=0
        f.seek(0)
        f.readline()
        dbl.pr2(r,'\n  Processing file: '+fname+'\n  Number of sequences: '+str(total))
        sd=defaultdict(int)
        if defined:
            matched=0
            par=[vrdic[k][4] for k in vrdic if k in vrs]
            while True:
                line=f.readline().rstrip()
                if not line:
                    break
                l=line.split('\t')[0].split(',')
                if args.remove_parent and len(vrlist[0])==6 and l==par:
                    continue
                m=line.split('\t')[1:]
                m[0]=int(m[0])
                for i in range(len(l)):
                    if 'X' in l[i]:
                        break
                    if len(l[i]) in sdf[i]:
                        break
                    for j in range(len(l[i])):
                        a=j+number+vrdic[vrs[i]][0]//3
                        if a in adf and l[i][j] in adf[a]:
                            a=0
                            break
                    if a==0:
                        break
                    b=m[0]/total*100
                    if (m[1]=="False" and b<ur) or b<freq[0] or m[0]<freq[1]:
                        break
                else:
                    filtered.append(line)
                    ftotal+=m[0]
                    if len(l)==1:
                        sd[len(l[0])]+=m[0]
                    if m[1]=='True':
                        matched+=m[0]
        else:
            seqs=defaultdict(int)
            while True:
                line=f.readline().rstrip()
                if not line:
                    break
                if args.remove_parent and line.count('(')==1 and line.count(',')==3:
                    continue
                l=line.split('\t')[0][1:-1].split('),(')
                l=[n.split(',') for n in l]
                m=int(line.split('\t')[1])
                x=l[-1]
                if len(x)==2:
                    z=int(x[0])+len(x[1])
                else:
                    z=int(x[0])+int(x[3])-int(x[2])
                if z in sdf:
                    continue
                b=m/total*100
                if b<freq[0] or m<freq[1] or z<length[2] or (length[3]>0 and z>length[3]):
                    continue
                x=[len(n[1]) for n in l if len(n)==2]
                y=0
                if x:
                    y=sum(x)
                if (npp>0 and y>npp) or (nps>0 and len(x)>nps):
                    continue
                filtered.append(line)
                ftotal+=m
                sd[z]+=m
                x=''
                for n in l:
                    if len(n)==2:
                        x+=n[1]
                    else:
                        if n[1] not in par:
                            print('\n  Unknown parent! Parental sequences must be those used to extract the sequences!\n')
                            sys.exit()
                        a,b,c,d=int(n[0]),n[1],int(n[2]),int(n[3])
                        i=l.index(n)
                        if i and len(l[i-1])==4:
                            c=c+int(l[i-1][0])+int(l[i-1][3])-int(l[i-1][2])-a
                        x+=par[b][c:d]






#####C CHECK number of lines in seqs and filtered is the same ! if not correct extract2
# create alignment with clustalw: temp file with concatenation of all parents and all seqs



                seqs[x]+=m
        f.close()
        if not filtered:
            continue
        if defined:
            x=fn+'_'+'-'.join(vrs)
        else:
            x=fname[:fname.rfind('_')]
        clf=x+'_cleaned.txt'
        f=open(clf,'w')
        f.write(str(ftotal)+'\n')
        for n in filtered:
            f.write(n+'\n')
        f.close()
        if not defined:
            x=fname[:fname.rfind('_')]
            slf=x+'_cleaned_seq.txt'
            f=open(slf,'w')
            f.write(str(ftotal)+'\n')
            for n in sorted(seqs,key=seqs.get,reverse=True):
                f.write(n+'\t'+str(seqs[n])+'\n')
            f.close()
        x=''
        if defined:
            x=' including '+str(matched)+' sequences perfectly matching the library'
        else:
            vrs='a'
        dbl.pr2(r,'  Discarded sequences: '+str(total-ftotal)+'\n  Filtered sequences: '+str(ftotal)+x)
        dbl.pr2(r,'  Complexity: '+str(len(filtered))+'\n  Filtered sequences were saved into file: '+clf)
        if not defined:
            dbl.pr2(r,'  '+str(len(seqs))+' full sequences were saved into file: '+slf)
        if len(vrs)==1:
            x=clf.replace('.txt','_sd.csv')
            f=open(x,'w')
            f.write('Size (aa)')
            for i in sorted(sd):
                f.write(','+str(i))
            f.write('\nNumber')
            for i in sorted(sd):
                f.write(','+str(sd[i]))
            f.close()
            dbl.pr2(r,'  Size distribution was saved into file: '+x)
            x=', '
            if defined:
                x=' aa (expected: '+str(len(vrdic[vrs[0]][2])//3)+' aa), '
            dbl.pr2(r,'  Most common size: '+str(max(sd,key=sd.get))+x+f'{(max(sd.values())/ftotal*100):.2f}'+'% of sequences')
        x=int(filtered[0].split('\t')[1])/ftotal*100
        dbl.pr2(r,'  Most common sequence: '+filtered[0].split('\t')[0]+', '+f'{(x):.2f}'+'% of sequences')
        if defined and len(vrlist[0])==6:
            M=[]
            for n in vrs:
                M.append(vrdic[n][4])
            M=tuple(M)
            if len(M)==1:
                M=M[0]
            else:
                M=','.join(M)
            if M==filtered[0].split('\t')[0]:
                dbl.pr2(r,'  Most common sequence is parent sequence')
            else:
                x=0
                for n in filtered:
                    if M==n.split('\t')[0]:
                        x=int(n.split('\t')[1])/ftotal*100
                        break
                dbl.pr2(r,'  Parent sequence: '+M+', '+f'{(x):.2f}'+'% of sequences')
        q=Counter([int(x.split('\t')[1]) for x in filtered])
        x=clf.replace('.txt','_cnd.csv')
        f=open(x,'w')
        f.write("Copy number,Number of sequences\n")
        for n in sorted(q):
            f.write(str(n)+","+str(q[n])+"\n")
        f.close()
        dbl.pr2(r,"  Copy number distribution was saved into file: "+x)
        if not defined or len(vrlist[0])==6:
            nummut=defaultdict(int)
            if not defined:
                numseg=defaultdict(int)
            for n in filtered:
                if defined:
                    x=0
                    m=n.split('\t')[0]
                    if len(m)!=len(M) or (',' in m and [i for i,j in enumerate(m) if j==',']!=[i for i,j in enumerate(M) if j==',']):
                        continue
                    for i in range(len(m)):
                        if m[i]!=M[i]:
                            x+=1
                else:
                    l=n.split('\t')[0][1:-1].split('),(')
                    l=[k.split(',') for k in l]
                    y=[len(k[1]) for k in l if len(k)==2]
                    x=0
                    if y:
                        x=sum(y)
                    numseg[len(y)]+=int(n.split('\t')[1])
                nummut[x]+=int(n.split('\t')[1])
            x=clf.replace('.txt','_mnd.csv')
            f=open(x,'w')
            f.write("Number of mutations,Number of sequences\n")
            n=0
            for k in sorted(nummut):
                f.write(str(k)+","+str(nummut[k])+"\n")
                n+=k*nummut[k]
            f.close()
            dbl.pr2(r,"  Average number of mutations per sequence: "+f'{(n/ftotal):.2f}')
            dbl.pr2(r,"  Mutation number distribution was saved into file: "+x)
            if not defined:
                x=clf.replace('.txt','_npsd.csv')
                f=open(x,'w')
                f.write("Number of non-parental segments,Number of sequences\n")
                n=0
                for k in sorted(numseg):
                    f.write(str(k)+","+str(numseg[k])+"\n")
                    n+=k*numseg[k]
                f.close()
                dbl.pr2(r,"  Average number of non-parental segments per sequence: "+f'{(n/ftotal):.2f}')
                dbl.pr2(r,"  Non-parental segment distribution was saved into file: "+x)
    if defined:
        for x in links:
            for y in files:
                if x[1] in y:
                    break
            else:
                continue
            for y in x[3]:
                if not dbl.check_file(x[1]+'_'+y+'_cleaned.txt',False):
                    break
            else:
                dbl.pr2(r,'\n  Analyzing variations for all variables positions in '+x[1])
                es=[]
                aaseq=[]
                for vr in x[3]:
                    es.append(len(vrdic[vr][2])//3)
                    f=open(x[1]+'_'+vr+'_cleaned.txt','r')
                    aaseq.append({})
                    f.readline().strip()
                    while True:
                        l=f.readline().rstrip()
                        if not l:
                            break
                        m=l.split('\t')
                        if m[0] not in aaseq[-1]:
                            aaseq[-1][m[0]]=[0,'']
                        aaseq[-1][m[0]][0]+=int(m[1])
                    f.close()
                aa_dist(aaseq,es,x[3],number,vrdic,x[1]+'_cleaned_aad.csv')
                dbl.pr2(r,'  Amino acid distribution of cleaned protein sequences of expected size was saved into file: '+x[1]+'_cleaned_aad.csv')
                if len(vrlist[0])==6:
                    dbl.pr2(r,'  Mutation distribution of cleaned protein sequences of expected size was saved into file: '+x[1]+'_cleaned_md.csv')
                continue
            dbl.pr2(r,'\n  Amino acid distribution file for '+x[1]+' can not be created because some cleaned files are missing!')
    r.close()
    print('\n  Cleaning report was saved in file: '+report+'\n')

def sizefilter(x,sdf,length):
    s=open(x,'r')
    sd=(s.readline().strip().split(',')[1:],s.readline().strip().split(',')[1:])
    for i in range(len(sd[0])):
        sd[0][i]=int(sd[0][i])
        sd[1][i]=int(sd[1][i])
    a=max(sd[1])
    b=sd[1].index(a)
    q=sum(sd[1])
    for i in range(len(sd[0])):
        if sd[1][i]/q*100<length[0] or sd[1][i]/sd[1][b]*100<length[1]:
            sdf[-1].append(sd[0][i])
    s.close()
    return sdf



##############  Correct extract2 to make complexity of filtered (condensed) and seqs (full) equal !!!


############################   UPDATE EXTRACT2 REPORT TO MAKE IT LIKE THE ONE FROM EXTRACT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def extract2(args):
    global comp,seq,par,noextract,fixed
# Check arguments
    print('\n  Checking arguments...',end='')
    if not args.parents:
        print('\n  Argument -p (--parents) is required!\n\n')
        sys.exit()
    par=glob(args.parents+'*')
    if len(par)>1:
        par=glob(args.parents+'.*')
    if not len(par):
        print('\n  Parent file could not be found!\n\n')
        sys.exit()
    if len(par)>1:
        print('\n  More than one match for parent file! Remove ambiguity by providing full file name\n\n')
        sys.exit()
    par=par[0]
    check_seq(par,'atgc','atgc',True,0)
    fp=args.forward_primer.lower().strip()
    rp=args.reverse_primer.lower().strip()
    for n in (fp,rp):
        for i in n:
            if i not in 'atgc'+ambiguous:
                print(i)
                print('\n  Wrong primer! "'+n+'" is not a nucleotide sequence!\n\n')
                sys.exit()
    if args.min_match<6:
        print('\n  Argument -m (--min_match) must be >5 !\n\n')
        sys.exit()
    args.error_correction=args.error_correction.lower()
    grain=args.crude_extract
# Detect reading frames and generate protein sequences
    print('                 OK\n\n  Processing parental sequences...',end='')
    par=dbl.getfasta(par,'atgc','atgc',True)
    par_aa={}
    save_par=False
    for n in sorted(par):
        temp=[]
        for i in (0,1,2):
            temp.append(dbl.transl(par[n][i:3*(len(par[n][i:])//3)+i]).strip().upper())
            temp[-1]=(temp[-1],temp[-1].find('*'))
        x=[k for k in temp if k[1]==-1]
        y=max([k[1] for k in temp])
        z=[k for k in temp if k[1]==y]
        if (len(x)>1 and len(par[n])%3!=0) or (len(x)==0 and len(z)>1):
            print('\n  Failed to detect reading frame for '+n+'. Sequence length should be a multiple of 3 and sequence should start with a complete codon to remove ambiguity!\n\n')
        if temp[0][1]==-1 and (len(par[n])%3==0 or par[n][:3]=='atg'):
            aaseq=temp[0][0]
            frame=0
        elif len(x)==1:
            aaseq=x[0][0]
            frame=[k[1] for k in temp].index(-1)
        else:
            aaseq=z[0][0]
            frame=[k[1] for k in temp].index(y)
            x=par[n][frame:3*(len(par[n][frame:])//3)+frame]
        if '*' in aaseq:
            x=x[:y*3]
            aaseq=aaseq[:y]
            if x!=par[n]:
                save_par=True
                par[n]=x
        par_aa[n]=aaseq
    if save_par:
        print('      OK\n')
        rename(args.parents)
        f=open(args.parents,'w')
        for n in sorted(par):
            f.write('>'+n+'\n'+par[n]+'\n')
        f.write('\n')
        f.close()
    x=args.parents
    if '.' in x:
        x=x[:x.rfind('.')]
    if len(x)>3 and x[-3] in ('-','_') and x[-2:]=='nt':
        x=x[:-3]
    fname=x+'_aa.fasta'
    r=open(x+'_extract_report.txt','w')
    f=open(fname,'w')
    for n in sorted(par_aa):
        f.write('>'+n+'\n'+par_aa[n]+'\n')
    f.write('\n')
    f.close()
    print('      OK\n')
    dbl.pr2(r,'  Parental protein sequences were saved into file: '+fname+'\n')
# Map primers to parents
    fpn=0
    rpn=0
    fpa=False
    rpa=False
    score=defaultdict(int)
    if rp:
        rprc=dbl.revcomp(rp)
    for n in par:
        if fp and fp in par[n]:
            score[n]+=1
        if rp and rprc in par[n]:
            score[n]+=1
    if score:
        x=max(score,key=score.get)
        ref=par[x]
    else:
        x=0
        ref=''
        for n in par:
            if len(par[n])>x:
                ref=par[n]
                x=len(par[n])
    if fp:
        fp2=fp[2:]
        cfp=dbl.compress(fp2)
        x=fp.find('atg')
        y=ref.find(fp)
        if ref[:3]=='atg':
            if x>=0 and fp[x:]==ref[:len(fp[x:])]:
                fpn=len(fp[x:])
            elif y==-1 and fp[-2:]=='at':
                fpn=2
            elif y==-1 and fp[-1]=='a':
                fpn=1
        if not fpn and y>=0:
            x=3-(y%3)
            if x==3:
                x=0
            fpn=len(fp)-x
        if len([k for k in fp2 if k in ambiguous])>0:
            fpa=True
    if rp:
        y=ref.rfind(rprc)
        if y!=-1:
            x=(y+len(rp))%3
            rpn=len(rp)-x
        else:
            i=1
            while i<len(rp) and rprc[:-i]!=ref[len(ref)-len(rp)+i:]:
                i+=1
            rpn=len(rprc[:-i])
        rp2=rprc[:-2]
        crp=dbl.compress(rp2)
        if len([k for k in rp2 if k in ambiguous])>0:
            rpa=True
# Start processing read files
    print('  Checking read files...')
    rfiles=findreadfiles(args.sequencing_reads,('atgc'+ambiguous,'atgc'),(args.parents,fname))
    for rfile in rfiles:
        y=np.arange(0,rfiles[rfile],rfiles[rfile]/1000)
        x=[round(n) for n in y]
        z=np.arange(0,100,0.1)
        y=[str(round(n,1)) for n in z]
        show=dict(zip(x,y))
        print('  Processing reads...       0.0%',end='')
        f,y,z,counter=initreadfile(rfile)
        seqs=defaultdict(int)
        total=0
        nodetect=0
        noextract=[0,0,0]
        extracted=0
        corrected=0
        correct=[0,0,0]
        while True:
            if total in show:
                k=show[total]
                print('\r  Processing reads...      '+' '*(4-len(k))+k+'%',end='')
            l,f,z,counter=getread(f,y,z,counter)
            if not l:
                break
            total+=1
# Detect correct strand
            if args.detect_strand:
                lrc=dbl.revcomp(l)
                d=False
                a=l[:len(l)//2]
                b=lrc[:len(lrc)//2]
                if fp and fp in a:
                    d=True
                if not d and fp and fp in b:
                    l=lrc
                    d=True
                if not d and rp and rp in a:
                    l=lrc
                    d=True
                if not d and rp and rp in b:
                    d=True
                if not d:
                    a=0
                    b=0
                    for i in range(0,len(l)-10,10):
                        for n in par:
                            if l[i:i+10] in par[n]:
                                a+=1
                            if lrc[i:i+10] in par[n]:
                                b+=1
                        if a>b*2:
                            break
                        if b>a*2:
                            l=lrc
                            break
                    else:
                        nodetect+=1
                        continue
# Process primer sequences
            if fp and not grain:
                if fp2 in l:
                    l=fp[:2]+l[l.find(fp2):]
                    l=l[len(fp)-fpn:]
                elif fpa:
                    for i in range(len(fp)):
                        if dbl.match(fp2,l[i:i+len(fp2)]):
                            l=fp[:2]+l[i:]
                            l=l[len(fp)-fpn:]
                            break
                else:
                    for i in range(len(fp2)):
                        k=0
                        j=-1
                        while k!=len(cfp):
                            j+=1
                            if len(l)>i+j>0 and l[i+j]==l[i+j-1]:
                                continue
                            if i+j<len(l) and l[i+j]!=cfp[k]:
                                break
                            k+=1
                        else:
                            break
                    if k==len(cfp):
                        n=1
                        while fp2[-n]==fp2[-n-1]:
                            n+=1
                        for k in range(1,n):
                            if l[i+j+k]!=l[i+j+k-1]:
                                break
                        l=fp[-fpn:]+l[i+j+k:]
                    else:
                        nodetect+=1
                        continue
            if rp and not grain:
                if rp2 in l:
                    l=l[:l.rfind(rp2)]+rprc[:rpn]
                elif rpa:
                    for i in range(len(rprc)):
                        if dbl.match(rp2,l[-i-len(rp2):-i]):
                            l=l[:-i-len(rp2)]+rprc[:rpn]
                            break
                else:
                    a=len(l)-len(rp)
                    if a<0:
                        nodetect+=1
                        continue
                    for i in range(len(rp2)):
                        k=0
                        j=-1
                        while k!=len(crp) and a-i+j+1<len(l):
                            j+=1
                            if 0<a-i+j and l[a-i+j]==l[a-i+j-1]:
                                continue
                            if a-i+j<len(l) and l[a-i+j]!=crp[k]:
                                break
                            k+=1
                        else:
                            break
                    if k==len(crp):
                        n=1
                        while rp2[n-1]==rp2[n]:
                            n+=1
                        m=1
                        while l[a-i+m]==l[a-i]:
                            m+=1
                        k=0
                        while k+m!=n:
                            if l[a-i]==l[a-i-k-1]:
                                k+=1
                            else:
                                break
                        l=l[:a-i-k]+rprc[:rpn]
                    else:
                        nodetect+=1
                        continue
# Match fragments to parent sequences
            comp=[]
            for n in par:
                ref=par[n]
                a=0
                b=min(args.min_match,len(l))
                while b<=len(l):
                    while b<=len(l) and l[a:b] not in ref:
                        a+=1
                        b+=1
                    if b>len(l):
                        break
                    while b<=len(l) and l[a:b] in ref:
                        b+=1
                    b-=1
                    C=[k.start() for k in regex.finditer(l[a:b],ref,overlapped=True)]
                    for c in C:
                        for m in comp:
                            if (m[0]<=a and m[1]>b) or (m[0]<a and m[1]>=b):
                                break
                        else:
                            temp=[k for k in comp if (k[0]>=a and k[1]<b) or (k[0]>a and k[1]<=b)]
                            for k in temp:
                                comp.remove(k)
                            comp.append((a,b,n,c,c+b-a))
                    a=b
                    b=a+args.min_match
            if not comp:
                nodetect+=1
                continue
# Remove useless matches
            comp.sort()
            temp=[k for k in comp]
            for i in range(1,len(temp)-1):
                if temp[i+1][0]<=temp[i-1][1] and temp[i][0]>temp[i-1][0] and temp[i+1][1]>temp[i][1]:
                    comp.remove(temp[i])
            for n in par:
                short=[k for k in comp if k[2]==n and k[1]-k[0]<19]
                if not short:
                    continue
                temp=[k[3]-k[0] for k in comp if k[2]==n and k[1]-k[0]>29]
                if not temp:
                    continue
                M=max(temp)
                m=min(temp)
                for s in short:
                    if s[3]-s[0]<m-9 or s[3]-s[0]>M+9:
                        comp.remove(s)
# Remove equivalent matches by minimizing parent switching
            temp=[k for k in comp]
            i=1
            j=1
            while i<len(temp)-j:
                if temp[i+j][0]-temp[i-1][1]>=3:
                    i+=1
                    continue
                while i+j+1<len(temp) and temp[i+j+1][0]-temp[i-1][1]<3:
                    j+=1
                a=[temp[k] for k in range(i,i+j) if temp[k][0:2]==temp[i-1][0:2]]
                b=[temp[k] for k in range(i,i+j) if temp[k][0:2]==temp[i+j][0:2]]
                x=''
                w=''
                if a and i>1 and temp[i-2][2] in [k[2] for k in a]:
                    x=temp.index([k for k in a if k[2]==temp[i-2][2]][0])
                elif a and not b and temp[i+j][2] in [k[2] for k in a]:
                    x=temp.index([k for k in a if k[2]==temp[i+j][2]][0])
                elif a and b and i+j+1<len(temp) and temp[i+j+1][2] in [k[2] for k in a]:
                    x=temp.index([k for k in a if k[2]==temp[i+j+1][2]][0])
                if b and i+j+1<len(temp) and temp[i+j+1][2] in [k[2] for k in b]:
                    w=temp.index([k for k in b if k[2]==temp[i+j+1][2]][0])
                elif b and not a and temp[i-1][2] in [k[2] for k in b]:
                    w=temp.index([k for k in b if k[2]==temp[i-1][2]][0])
                elif b and a and i>1 and temp[i-2][2] in [k[2] for k in b]:
                    w=temp.index([k for k in b if k[2]==temp[i-2][2]][0])
                if x:
                    temp[x],temp[i-1]=temp[i-1],temp[x]
                if w:
                    temp[w],temp[i+j]=temp[i+j],temp[w]
                for k in range(i,i+j):
                    comp.remove(temp[k])
                i=i+j+1
                j=1
            comp.sort()
# Crude extraction mode
            if grain:
                seq=[]
                for i in range(len(comp)):
                    if i:
                        x=comp[i-1][1]
                    else:
                        x=0
                    if comp[i][0]-x>grain/2:
                        seq.append(('unmatched',round((comp[i][0]-x)/grain)))
                    if comp[i][1]-comp[i][0]>grain/2:
                        seq.append((comp[i][2],round((comp[i][1]-comp[i][0])/grain)))
                if len(l)-comp[-1][1]>grain/2:
                    seq.append(('unmatched',round((len(l)-comp[-1][1])/grain)))
                seq2=[]
                p=''
                a=0
                for i in range(len(seq)):
                    if seq[i][0]!=p:
                        if p:
                            seq2.append((p,a))
                        p=seq[i][0]
                        a=seq[i][1]
                    else:
                        a+=seq[i][1]
                seq2.append((p,a))
                seqs[tuple(seq2)]+=1
                extracted+=1
                continue
# Refine mapping of unmapped regions to account for insertions or substitutions
            temp=[k for k in comp]
            for j in (1,-1):
                for i in range(len(temp)):
                    k=len(temp)-1
                    if j==-1:
                        k=0
                    a=temp[i][int(j>0)]
                    if a<2 or a>len(l)-2:
                        continue
                    if j*i<j*k and ((temp[i+j][2]==temp[i][2] and j==-1) or j*temp[i+j][int(j<0)]<j*a+7):
                        continue
                    ref=par[temp[i][2]]
                    c=temp[i][4-int(j<0)]-j*2
                    if j==1 and i==len(temp)-1:
                        e=len(l)
                    elif j==-1 and i==0:
                        e=0
                    elif temp[i+j][2]!=temp[i][2]:
                        e=temp[i+j][int(j>0)]
                    else:
                        e=temp[i+j][int(j<0)]
                    e2=max(0,j*len(ref))
                    b=abs(min(e,j*(a+j*6)))
                    d=abs(min(j*(c+j*7),e2))
                    if abs(b-a)<3:
                        continue
                    while j*b<=j*e:
                        while j*b<=j*e and j*a<j*b and j*c<j*d and l[min(a,b):max(a,b)] not in ref[min(c,d):max(c,d)]:
                            a+=j
                            b+=j
                            c+=j
                            if d!=e2:
                                d+=j
                        if j*b>j*e or j*a>=j*b or j*c>=j*d :
                            break
                        while j*b<=j*e and l[min(a,b):max(a,b)] in ref[min(c,d):max(c,d)]:
                            b+=j
                            if d!=e2:
                                d+=j
                        b-=j
                        if j==1:
                            c=ref.find(l[a:b],c,d)
                        else:
                            c=ref.rfind(l[b:a],d,c)+a-b
                        comp.append((min(a,b),max(a,b),temp[i][2],min(c,c+b-a),max(c,c+b-a)))
                        if j*i<j*k and j*comp[-1][int(j>0)]+5>=j*temp[i+j][int(j<0)]:
                            break
                        c=c+b-a-j*2
                        d=abs(min(j*(c+j*7),e2))
                        a=b
                        b=abs(min(e,j*(a+j*6)))
                        if abs(b-a)<3:
                            break
# Correct sequencing errors
            comp.sort()
            if 'f' in args.error_correction or 'a' in args.error_correction or 's' in args.error_correction:
                dels=[]
                fixed=[0,0,0]
                for n in par:
                    temp=[i for i in range(len(comp)) if comp[i][2]==n]
                    ref=par[n]
                    if len(temp)<2:
                        continue
                    for i in range(1,len(temp)):
                        fix=False
                        w=comp[temp[i-1]][1]
                        a=comp[temp[i-1]][4]
                        x=comp[temp[i]][0]
                        b=comp[temp[i]][3]
                        if 'f' in args.error_correction and temp[i]==temp[i-1]+1 and ((a==b and x==w+1) or (w==x and b==a+1) or (w==x and b==a-1)):
                            fix=True
                            fixed[0]=1
                        elif 'a' in args.error_correction and x==w+1 and b==a+1 and l[w] in ambiguous:
                            fix=True
                            fixed[1]=1
                        elif 's' in args.error_correction and x==w+1 and b==a+1 and l[w] in 'tga':
                            q=b%3
                            if not q:
                                q=3
                            if l[x-q:x-q+3] in ('taa','tag','tga'):
                                fix=True
                                fixed[2]=1
                        if fix:
                            comp[temp[i]]=(comp[temp[i-1]][0],comp[temp[i]][1],n,comp[temp[i-1]][3],comp[temp[i]][4])
                            dels.append(temp[i-1])
                fix=False
                n=comp[0][2]
                ref=par[n]
                a=comp[0][0]
                c=comp[0][3]
                x=min(a,c)
                w=c-1-max(c-1-x,0)
                if a and c and 'f' in args.error_correction:
                    if l[a-w:a]==ref[c-1-w:c-1]:
                        comp[0]=(a-w,comp[0][1],n,c-1-w,comp[0][4])
                        fix=True
                        fixed[0]=1
                    elif l[a-1-w:a-1]==ref[c-w:c]:
                        comp[0]=(a-1-w,comp[0][1],n,c-w,comp[0][4])
                        fix=True
                        fixed[0]=1
                if not fix and a and c and 'a' in args.error_correction and l[a-1] in ambiguous and (l[a-x:a-1]==ref[c-x:c-1] or a==1):
                    comp[0]=(a-x,comp[0][1],n,c-x,comp[0][4])
                    fix=True
                    fixed[1]=1
                if not fix and a and c and 's' in args.error_correction and l[a-1] in 'tga' and (l[a-x:a-1]==ref[c-x:c-1] or a==1):
                    w=c%3
                    if not w:
                        w=3
                    if l[a-w:a-w+3] in ('taa','tag','tga'):
                        comp[0]=(a-x,comp[0][1],n,c-x,comp[0][4])
                        fix=True
                        fixed[2]=1
                fix=False
                n=comp[-1][2]
                ref=par[n]
                a=comp[-1][1]
                c=comp[-1][4]
                if a!=len(l) and c!=len(ref):
                    x=min(len(l)-a,len(ref)-c)
                    if 'f' in args.error_correction:
                        w=min(c+1+x,len(ref))-c-1
                        if l[a:a+w]==ref[c+1:c+1+w]:
                            comp[-1]=(comp[-1][0],a+w,n,comp[-1][3],c+1+w)
                            fix=True
                            fixed[0]=1
                        w=min(a+1+x,len(l))-a-1
                        if l[a+1:a+1+w]==ref[c:c+w]:
                            comp[-1]=(comp[-1][0],a+1+w,n,comp[-1][3],c+w)
                            fix=True
                            fixed[0]=1
                    if not fix and 'a' in args.error_correction and l[a] in ambiguous and (l[a+1:a+x]==ref[c+1:c+x] or a==len(l)-1):
                        comp[-1]=(comp[-1][0],a+x,n,comp[-1][3],c+x)
                        fix=True
                        fixed[1]=1
                    if not fix and 's' in args.error_correction and l[a] in 'tga' and (l[a+1:a+x]==ref[c+1:c+x] or a==len(l)-1):
                        w=c%3
                        if not w:
                            w=3
                        if l[a-w+1:a-w+4] in ('taa','tag','tga'):
                            comp[-1]=(comp[-1][0],a+x,n,comp[-1][3],c+x)
                            fix=True
                            fixed[2]=1
                dels.sort(reverse=True)
                for i in dels:
                    del comp[i]
# Clean trash
            comp.sort()
            while True:
                for i in range(1,len(comp)):
                    if (comp[i-1][0]<=comp[i][0] and comp[i-1][1]>comp[i][1]) or (comp[i-1][0]<comp[i][0] and comp[i-1][1]>=comp[i][1]):
                        del comp[i]
                        break
                    if comp[i-1][0]==comp[i][0] and comp[i-1][1]==comp[i][1]:
                        for n in sorted(par):
                            if n in comp[i][2]:
                                del comp[i-1]
                                break
                            if n in comp[i-1][2]:
                                del comp[i]
                                break
                        break
                    if comp[i][0]-comp[i-1][0]<4 and comp[i][1]>comp[i-1][1] and comp[i-1][1]-comp[i-1][0]<13:
                        del comp[i-1]
                        break
                else:
                    break
# Process 5' end
            global fs
            fs=False
            seq=[]
            a2=''
            a=l[:comp[0][0]]
            if comp[0][0]!=0 and comp[0][3]!=0:
                if comp[0][0]>=comp[0][3]:
                    a2=a[comp[0][0]-comp[0][3]:]
                else:
                    a2=a[(len(a)-comp[0][3]%3)%3:]
            if comp[0][0]==0 and par[comp[0][2]][:3]=='atg' and 0<comp[0][3]<4:
                comp[0]=(0,comp[0][1],comp[0][2],0,comp[0][4])
            c=process('',a2,0)
            if not c[0]:
                continue
            x=c[1]
# Process internal fragments
            for i in range(1,len(comp)):
                a1=par[seq[-1][1]][comp[i-1][4]-x:comp[i-1][4]]
                a2=l[comp[i-1][1]:comp[i][0]]
                c=process(a1,a2,i)
                if not c[0]:
                    break
                x=c[1]
            if not c[0]:
                continue
# Process 3' end
            a=par[seq[-1][1]][comp[-1][4]-x:comp[-1][4]]+l[comp[-1][1]:]
            a=a[:(len(a)//3)*3]
            a=dbl.transl(a)
            if '*' in a:
                a=a[:a.find('*')]
            if a:
                c=seq[-1][0]+seq[-1][3]-seq[-1][2]
                seq.append((c,a))
# Check sequence
            broke=False
            for i in range(1,len(seq)):
                if len(seq[i-1])==4:
                    x=seq[i-1][0]+seq[i-1][-1]-seq[i-1][-2]
                if len(seq[i])==len(seq[i-1])==4 and seq[i][0]<x:
                    if par_aa[seq[i-1][1]][seq[i-1][3]-x+seq[i][0]:seq[i-1][3]]!=par_aa[seq[i][1]][seq[i][2]:seq[i][2]+x-seq[i][0]]:
                        noextract[0]+=1
                        broke=True
                        break
                if len(seq[i])==2:
                    for j in range(1,len(seq[i][1])+1):
                        if seq[i-1][3]-1+j>=len(par_aa[seq[i-1][1]]):
                            j-=1
                            break
                        if par_aa[seq[i-1][1]][seq[i-1][3]:seq[i-1][3]+j]!=seq[i][1][:j]:
                            j-=1
                            break
                    if j:
                        seq[i-1]=(seq[i-1][0],seq[i-1][1],seq[i-1][2],seq[i-1][3]+j)
                        seq[i]=(seq[i][0]+j,seq[i][1][j:])
            for i in range(len(seq)-1):
                if len(seq[i])==2 and seq[i][1]:
                    for j in range(1,len(seq[i][1])+1):
                        if seq[i+1][2]-j<0:
                            j-=1
                            break
                        if par_aa[seq[i+1][1]][seq[i+1][2]-j:seq[i+1][2]]!=seq[i][1][-j:]:
                            j-=1
                            break
                    if j:
                        seq[i+1]=(seq[i+1][0]-j,seq[i+1][1],seq[i+1][2]-j,seq[i+1][3])
                        seq[i]=(seq[i][0],seq[i][1][:-j])
            seq=[k for k in seq if k[1]]
            seq.sort()
            for i in range(len(seq)):
                if len(seq[i])==2 and len(seq[i][1])>3:
                    xa={}
                    xb={}
                    wa={}
                    wb={}
                    for n in par_aa:
                        for j in range(len(seq[i][1])-3):
                            if j and 0 in wa.values():
                                break
                            a=0
                            b=0
                            if n not in wb and seq[i][1][j:] in par_aa[n]:
                                wb[n]=j
                                if i<len(seq)-1:
                                    for b in range(1,seq[i+1][3]-seq[i-1][2]):
                                        if seq[i][1][j:]+par_aa[seq[i+1][1]][seq[i+1][2]:seq[i+1][2]+b] not in par_aa[n]:
                                            b-=1
                                            break
                                xb[n]=b
                            if j:
                                w=seq[i][1][:-j]
                            else:
                                w=seq[i][1]
                            if n not in wa and w in par_aa[n]:
                                wa[n]=j
                                if i:
                                    for a in range(1,seq[i-1][3]-seq[i-1][2]):
                                        if par_aa[seq[i-1][1]][seq[i-1][3]-a:seq[i-1][3]]+w not in par_aa[n]:
                                            a-=1
                                            break
                                xa[n]=a
                            if n in wa and n in wb:
                                break
                    q=[k for k in wb if not wb[k]]
                    if q:
                        q=sorted(q,key=lambda k:(xa[k]+xb[k]),reverse=True)
                        n,a,b=q[0],xa[q[0]],xb[q[0]]
                        q=seq[i][1]
                        if i:
                            q=par_aa[seq[i-1][1]][seq[i-1][3]-a:seq[i-1][3]]+q
                        if i<len(seq)-1:
                            q+=par_aa[seq[i+1][1]][seq[i+1][2]:seq[i+1][2]+b]
                        c=par_aa[n].find(q)
                        seq[i]=(seq[i][0]-a,n,c,c+len(q))
                        continue
                    if wb:
                        a=min(wb.values())
                        q=[k for k in wb if wb[k]==a]
                        if len(q)>1:
                            q=sorted(q,key=lambda k:xb[k],reverse=True)
                        n,b,j=q[0],xb[q[0]],wb[q[0]]
                        q=seq[i][1][j:]
                        if b:
                            q+=par_aa[seq[i+1][1]][seq[i+1][2]:seq[i+1][2]+b]
                        c=par_aa[n].find(q)
                        seq.append((seq[i][0]+j,n,c,c+len(q)))
                        seq[i]=(seq[i][0],seq[i][1][:j])
                    if wa:
                        a=min(wa.values())
                        q=[k for k in wa if wa[k]==a]
                        if len(q)>1:
                            q=sorted(q,key=lambda k:xa[k],reverse=True)
                        n,a,j=q[0],xa[q[0]],wa[q[0]]
                        q=seq[i][1][:-j]
                        if a:
                            q=par_aa[seq[i-1][1]][seq[i-1][3]-a:seq[i-1][3]]+q
                        c=par_aa[n].find(q)
                        seq.append((seq[i][0]-a,n,c,c+len(q)))
                        seq[i]=(seq[i][0]+len(seq[i][1])-j,seq[i][1][-j:])
            if broke:
                continue
            seq=[k for k in seq if k[1]]
            seq.sort()
            while True:
                for i in range(1,len(seq)):
                    if len(seq[i-1])==len(seq[i])==4 and seq[i-1][0]+seq[i-1][3]-seq[i-1][2]>=seq[i][0]+seq[i][3]-seq[i][2]:
                        del seq[i]
                        break
                    if len(seq[i-1])==len(seq[i])==4 and seq[i-1][1]==seq[i][1]:
                        seq[i-1]=(seq[i-1][0],seq[i-1][1],seq[i-1][2],seq[i][3])
                        del seq[i]
                        break
                    if len(seq[i-1])==len(seq[i])==4 and par_aa[seq[i-1][1]][seq[i-1][3]:seq[i][3]-seq[i][2]+seq[i-1][2]+seq[i][0]-seq[i-1][0]]==par_aa[seq[i][1]][seq[i][2]+seq[i-1][3]-seq[i-1][2]-seq[i][0]+seq[i-1][0]:seq[i][3]]:
                            seq[i-1]=(seq[i-1][0],seq[i-1][1],seq[i-1][2],seq[i-1][2]+seq[i][0]-seq[i-1][0]+seq[i][3]-seq[i][2])
                            del seq[i]
                            break
                    elif len(seq[i-1])==len(seq[i])==4 and par_aa[seq[i][1]][seq[i][2]-seq[i][0]+seq[i-1][0]:seq[i][2]-seq[i][0]+seq[i-1][0]+seq[i-1][3]-seq[i-1][2]]==par_aa[seq[i-1][1]][seq[i-1][2]:seq[i-1][3]]:
                            seq[i]=(seq[i-1][0],seq[i][1],seq[i][2]-seq[i][0]+seq[i-1][0],seq[i][3])
                            del seq[i-1]
                            break
                else:
                    break
            for i in range(len(seq)):
                if len(seq[i])==2:
                    continue
                for n in sorted(par_aa):
                    if n==seq[i][1]:
                        break
                    a=0
                    b=len(par_aa[n])
                    for j in range(1,i+1):
                        if i>0 and seq[i-j][1]==n:
                            a=seq[i-j][3]
                    for j in range(i+1,len(seq)):
                        if seq[j][1]==n:
                            b=seq[j][2]
                    c=par_aa[n].find(par_aa[seq[i][1]][seq[i][2]:seq[i][3]],a,b)
                    if c!=-1:
                        seq[i]=(seq[i][0],n,c,c+seq[i][3]-seq[i][2])
                        break
# Store sequence
            seqs[tuple(seq)]+=1
            extracted+=1
            if sum(fixed)>0:
                corrected+=1
                correct[0]+=fixed[0]
                correct[1]+=fixed[1]
                correct[2]+=fixed[2]
        f.close()
# Save sequences and distributions to files
        a=len(str(total))
        b=str(nodetect+sum(noextract))
        c=str(nodetect)
        d=str(noextract[0])
        e=str(noextract[1])
        f=str(noextract[2])
        print('\b\b\b\b\b\b100.0%\n\n')
        dbl.pr2(r,'  Read file: '+rfile)
        dbl.pr2(r,'  Reads processed: '+str(total))
        dbl.pr2(r,'  Reads discarded: '+' '*(a-len(b))+b+' ('+str(round((nodetect+sum(noextract))/total*100,2))+'%) including:\n'+' '*(19+a-len(c))+c+' unmatched\n'+' '*(19+a-len(d))+d+' frameshifted reads\n'+' '*(19+a-len(e))+e+' reads with ambiguous nucleotides\n'+' '*(19+a-len(f))+f+' reads with stop codons')
        b=str(corrected)
        c=str(correct[0])
        d=str(correct[1])
        e=str(correct[2])
        dbl.pr2(r,'  Reads extracted: '+' '*(a-len(str(extracted)))+str(extracted)+' ('+str(round((extracted)/total*100,2))+'%) including:\n'+' '*(19+a-len(b))+b+' total corrected reads\n'+' '*(19+a-len(c))+c+' reads with corrected frameshift\n'+' '*(19+a-len(d))+d+' reads with corrected ambiguous nucleotide\n'+' '*(19+a-len(e))+e+' reads with corrected stop codon\n')
        fname=rfile[:rfile.find('.')]
        if not '.' in rfile:
            fname=rfile
        if grain:
            fname+='_crude-'+str(grain)+'.txt'
        else:
            fname+='_extracted.txt'
        f=open(fname,'w')
        f.write(str(extracted)+'\n')
        sd=defaultdict(int)
        npp=defaultdict(int)
        nps=defaultdict(int)
        for n in sorted(seqs.items(), reverse=True, key=lambda k: k[1]):
            x=str(n[0])[1:-1].replace("'",'').replace(' ','')+'\t'+str(n[1])+'\n'
            f.write(x.replace(',\t','\t'))
            a=n[0][-1]
            if len(a)!=2:
                b=a[0]+a[3]-a[2]
            elif isinstance(a[1],int):
                b=round(sum([k[1] for k in n[0]])*grain/3)
            else:
                b=a[0]+len(a[1])
            sd[b]+=n[1]
            if grain:
                continue
            npp[sum([len(k[1]) for k in n[0] if len(k)==2])]+=n[1]
            nps[len([k for k in n[0] if len(k)==2])]+=n[1]
        f.close()
        dbl.pr2(r,'  Extracted sequences were saved into file: '+fname)
        fname=fname.replace('.txt','_sd.csv')
        f=open(fname,'w')
        f.write('Size (aa)')
        for i in sorted(sd):
            f.write(','+str(i))
        f.write('\nNumber')
        for i in sorted(sd):
            f.write(','+str(sd[i]))
        f.write('\n')
        f.close()
        dbl.pr2(r,'  Size distribution was saved into file: '+fname)
        if not grain:
            fname=fname.replace('_sd.','_mnd.')
            f=open(fname,'w')
            f.write('Number of non-parental positions,Number of reads\n')
            for i in sorted(npp):
                f.write(str(i)+','+str(npp[i])+'\n')
            f.close()
            dbl.pr2(r,'  Distribution of numbers of non-parental positions was saved into file: '+fname)
            fname=fname.replace('_mnd.','_npsd.')
            f=open(fname,'w')
            f.write('Number of non-parental segments,Number of reads\n')
            for i in sorted(nps):
                f.write(str(i)+','+str(nps[i])+'\n')
            f.close()
            dbl.pr2(r,'  Distribution of numbers of non-parental segments was saved into file: '+fname+'\n')
    r.close()






  ###TABLE
# File name prefix
# Total reads
# Nodetect reads
# Noextract reads incl frameshifted, ambiguous, stop
# extracted reads
# % fixed reads
# nb fixed framsehifts / ambiguous / stop codons
# Complexity
# average seq length
# Most common length: size + %
# shortest seq
# largest seq
# Total nb parents
# average nb of parents per seq
# Main parent
# % wt for each parent / total
# % MUTANT
# % aa coverage for each parent
# Average non-parent aa coverage
# Average nb of segments per seq

# init / link to assign parent lists and primers to each read file (different parent list and primers for each read file)
           # -> each parent has its own file, each read file has its own parent list file (with parent names only)
# create caplib3.conf file to be used by clean and compare ?
# modify COMPARE to compare EXTRACT2 data ->




def process(a1,a2,i):
    global seq,noextract,comp,fs
    a=a1+a2
    p=3-comp[i][3]%3
    b=''
    if p!=3:
        b=par[comp[i][2]][comp[i][3]:comp[i][3]+p]
    else:
        p=0
    if not i and not a:
        z=0
        b=''
    elif not i and a:
        z=len(a+b)
    elif i and not a2 and fixed:
        w=comp[i-1][1]-comp[i][0]-2
        z=par[comp[i-1][2]].find(par[comp[i][2]][comp[i][3]:comp[i][3]+w],comp[i-1][4]-w-4)
        if z==-1 and not fs:
            comp[i],comp[i-1]=comp[i-1],comp[i]
            fs=True
            return (True,len(a1))
        if z==-1 and fs:
            noextract[0]+=1
            return (False,0)
        z=z+p-comp[i-1][4]+len(a1)
    else:
        z=comp[i][0]+p-comp[i-1][1]+len(a1)
    if z%3!=0 and not fs:
        comp[i],comp[i-1]=comp[i-1],comp[i]
        fs=True
        return (True,len(a1))
    if z%3!=0 and fs:
        noextract[0]+=1
        return (False,0)
    c=0
    if seq:
        c=seq[-1][0]+seq[-1][3]-seq[-1][2]
    if z>0:
        w=dbl.transl(a[:z]+b[min(0,p-z+len(a[:z])):])
        if 'X' in w:
            noextract[1]+=1
            return (False,0)
        if '*' in w:
            noextract[2]+=1
            return (False,0)
        seq.append((c,w))
    c+=z//3
    x=comp[i][4]%3
    seq.append((c,comp[i][2],(comp[i][3]+p)//3,(comp[i][4]-x)//3))
    return (True,x)

def initreadfile(rfile):
    if rfile[-3:]=='.gz':
        f=gzip.open(rfile,'rt')
    else:
        f=open(rfile,'r')
    l=f.readline().strip()
    if not l or l[0] not in ('>','@'):
        f.close()
        print('  '+rfile+' does not look like a fastq or fasta file.\n')
        sys.exit()
    if l[0]=='>':
        l=f.readline().strip()
        l=f.readline().strip()
        if l and l[0]=='>':
            y=2
        else:
            y=0
    else:
        y=4
    f.seek(0)
    z=y-2
    counter=0
    return f,y,z,counter

def getread(f,y,z,counter):
    if not y:
        l=''
        while True:
            line=f.readline().strip()
            if not line:
                line=f.readline().strip()
            if not line or (l and line[0]=='>'):
                break
            if not l and line[0]=='>':
                continue
            l+=line
    else:
        while z<y:
            l=f.readline().strip()
            z+=1
    if not l:
        return l,f,z,counter
    l=l.lower()
    z=0
    counter+=1
    return l,f,z,counter

def findreadfiles(pattern,seqtype,exclude):
    if pattern=='auto':
        x='*.f*'
    elif dbl.check_file(pattern,False):
        x=pattern
    else:
        x=pattern+'*'
    rfiles=glob(x)
    if len(rfiles)>1:
        rfiles=[x for x in rfiles if (len(x)>5 and x[-5:] in ('fasta','fastq','fa.gz','fq.gz')) or (len(x)>3 and x[-3:] in ('.fa','.fq')) or (len(x)>8 and x[-8:] in ('fasta.gz','fastq.gz'))]
    rfiles=[x for x in rfiles if check_seq(x,seqtype[0],seqtype[1],False,5)]
    if not rfiles:
        print("\n  No read file found. Check pattern, or move to correct directory, or include path in pattern.\n")
        sys.exit()
    for n in exclude:
        if n and n in rfiles:
            rfiles.remove(n)
    rfiles=dict.fromkeys(rfiles,0)
    for rfile in rfiles:
        if rfile[-3:]=='.gz':
            f=gzip.open(rfile,'r')
        elif rfile[-1]=='q':
            f=open(rfile,'rb')
        else:
            f=open(rfile,'r')
        if rfile[-3:]=='.gz' or rfile[-1]=='q':
            nr=dbl.lncount(f)//4
        else:
            nr=f.read().count('>')
        f.close()
        rfiles[rfile]=nr
    print('  Read file(s) (number of reads):')
    for n in rfiles:
        print('  '+n+' ('+str(rfiles[n])+')')
    print()
    return rfiles

def mix(args):
    if args.new:
        rename('caplib3_mix.txt')
    if glob('caplib3_mix.txt'):
        input,ratio,output=readmix('')
        _,parent=get_parent()
        data=[]
        legend=[]
        for i in range(len(input)):
            data.append([])
            for j in range(len(input[i])):
                x=glob(input[i][j]+'_cleaned_*.csv')
                if not x:
                    x=glob(input[i][j]+'_aad.csv')+glob(input[i][j]+'_aad.csv')
                    if not x:
                        x=glob(input[i][j])
                        if not x:
                            print('  '+input[i][j]+' not found!\n\n')
                            sys.exit()
                if not data[-1]:
                    for n in x:
                        data[-1].append({})
                if not legend:
                    for n in x:
                        legend.append('')
                for k in range(len(x)):
                    g=open(x[k],'r')
                    y=[line.strip().split(',') for line in g]
                    g.close()
                    if len(y)<2:
                        print('  The file '+input[i][j]+' does not contain any data!\n\n')
                        sys.exit()
                    if legend[k] and y[0]!=legend[k]:
                        print('  Wrong file type! Input files to be combined must have same structure!\n\n')
                        sys.exit()
                    if not legend[k]:
                        legend[k]=y[0]
                    for m in y[1:]:
                        if m[0] in data[-1][k]:
                            print('  Data from same library (same line under INPUT) must have different positions!\n\n')
                            sys.exit()
                        data[-1][k][m[0]]=m[1:]
            if len(data)>1 and len(data[-1])!=len(data[-2]):
                print('  The same number of different file types (aad / md) must exist for each library!\n\n')
                sys.exit()
        mix=[]
        for j in range(len(data[0])):
            mix.append({})
            if legend[j][0]=='Position':
                x='_md.csv'
            else:
                x='_aad.csv'
            if '.csv' in output and len(legend)==1:
                x=''
            fname=output+x
            g=open(fname,'w')
            g.write(','.join(legend[j])+'\n')
            for k in sorted(set([y for x in [n[j].keys() for n in data] for y in x])):
                x=[]
                for l in range(len(legend[j][1:])):
                    x.append(0)
                    for i in range(len(data)):
                        if k in data[i][j]:
                            x[-1]+=float(data[i][j][k][l])*ratio[i]
                        elif not legend[j][0]:
                            if aa[l]==parent[int(k)-1]:
                                x[-1]+=ratio[i]
                x=[str(n) for n in x]
                g.write(k+','+','.join(x)+'\n')
            g.close()
            print('\n  File '+fname+' successfully created!')
        print()
        return
    f=open('caplib3_mix.txt','w')
    f.write('# INPUT\nInstructions: each line is a different library (and can have multiple files separated by blank spaces), no need to write full file names, use prefix instead.\n\n')
    f.write('# RATIO\nInstructions: write one number per line, in the same order as the libraries in the previous section.\n\n')
    f.write('# OUTPUT\nInstructions: write prefix of mix output files (full file names will be created automatically).\n\n')
    f.close()
    x=glob('*cleaned_aad.csv')+glob('*cleaned_md.csv')
    x=sorted(set([n[:n.rfind('_cleaned_')] for n in x]))
    print('  Existing data prefixes in current directory:')
    print('\n  '+'\n  '.join(x)+'\n')
    print('  Edit the file caplib3_mix.txt before running caplib3 mix (without argument to process the edited file)!\n\n')

def get_parent():
    dbl.check_file('caplib3.conf',True)
    g=open('caplib3.conf','r')
    x=1
    for l in g:
        if not x:
            x=l.strip()
            break
        if l[:16]=='# Parent protein':
            x=0
    dbl.check_file(x,True)
    y=readseq(x).upper()
    g.close()
    return x,y

def compare(args):
    global vrlist,links,number,pp,lt
    if args.new:
        rename('caplib3_compare.txt')
        rename('compare_table.csv')
    format=dbl.check_plot_format(args.file_format)
    vrlist,links,number,pp,lt=readinit('extract')
    if args.input_files=='auto':
        x='*.*'
        if glob('caplib3_compare.txt'):
            compare2(format)
            return
    else:
        x=args.input_files
    files=glob(x)
    files=[n for n in files if ('report.txt' in n or 'cleaned' in n or 'design' in n or 'complexity' in n or '_crude-' in n)]
    if not '.csv' in x and len([n for n in files if 'clean_report.txt' in n])==0:
        files.extend(glob('All_clean_report.txt'))
    if not files:
        print("\n  Files not found. Check pattern, or move to correct directory, or include path in pattern.\n")
        sys.exit()
    rename('caplib3_compare.txt')
    f=open('caplib3_compare.txt','w')
    s=[n[:-16] for n in files if ('cleaned_cnd.csv' in n)]
    temp=[]
    for n in links:
        if [x for x in s if n[1] in x]:
            for m in n[3]:
                if n[1]+'_'+m in s:
                    temp.append(n[1]+'_'+m)
            if len(n)>4:
                temp.append([x for x in s if (n[1] in x and '-' in x[x.rfind('_'):])][0])
    for n in s:
        if not n in temp:
            temp.append(n)
    s=list(temp)
    if len(s)>0:
        s0=[n[:n.rfind('_')] for n in s]
        s1=sorted(set([n[max(n.rfind('-')+1,n.rfind('_')+1):] for n in s0]))
        s2=[n[:n.rfind('_')][:max(n[:n.rfind('_')].rfind('-')+1,n[:n.rfind('_')].rfind('_')+1)]+'?'+n[n.rfind('_'):] for n in s]
        temp=[]
        for i in s2:
            if i not in temp:
                temp.append(i)
        s2=temp
        s3={}
        for x in s2:
            s3[x]=[]
            for n in s1:
                if x.replace('?',n) in s:
                    s3[x].append(1)
                else:
                    s3[x].append(0)
        s4=sorted(set([tuple(s3[n]) for n in s3]))
        s5=[]
        s6=[]
        q=1
        for n in s4:
            if sum(n)==1:
                temp=[x[x.rfind('_')+1:] for x in s3 if tuple(s3[x])==n]
                q=len(set(temp))
                if q==len(temp):
                    s5.append([x.replace('?',s1[s3[x].index(1)]) for x in s2 if tuple(s3[x])==n])
                else:
                    s6.append([x.replace('?',s1[s3[x].index(1)]) for x in s2 if tuple(s3[x])==n])
        f.write('### DATA CLEANING ###\n')
        f.write('Instructions: Each group surrounded by empty lines will be a separate chart.\n\n')
        if vrlist:
            y=0
            for i in range(len(s)):
                x=''
                y+=1
                if y>25 and i+1!=len(s) and s[i][:s[i].rfind('_')]!=s[i+1][:s[i+1].rfind('_')]:
                    x='\n'
                    y=0
                f.write(s[i]+'\n'+x)
            if not x:
                f.write('\n')
        A=('### CLUSTER CARDINALITY DISTRIBUTION ###\n','### PROTEIN COMPLEXITY ###\n')
        B=('Instructions: Each group surrounded by empty lines will be a separate chart. Data in same line (separated by blank space) will have same color and different symbol (10 max). Data in different lines will have different color (10 max).\n\n','Instructions: Each group surrounded by empty lines will be a separate chart. Data in same line (separated by blank space) will have different colors and will be grouped together.\n\n')
        C=(3,25)
        design=''
        n=glob('*-complexity.txt')
        if len(n)==1:
            design=n[0].replace('-complexity.txt','_design')
        for c in range(2):
            a=0
            s7=[]
            f.write(A[c])
            f.write(B[c])
            if s6 and not s5:
                ccd(s6,f,C[c])
            for n in s5:
                if not s7:
                    s7.append(n)
                    continue
                a=[x[x.rfind('_'):] for x in s7[0]]
                if [x[x.rfind('_'):] for x in n]==a:
                    s7.append(n)
                elif len(s7)==1:
                    s7[0].extend(n)
                else:
                    ccd([n],f,C[c])
            if s6 and s5:
                s7.append([])
                a=[x[x.rfind('_'):] for x in s7[0]]
                for n in s6:
                    for j in range(0,len(n),len(s7[0])):
                        if a==[x[x.rfind('_'):] for x in n[j:j+len(s7[0])]]:
                            s7[-1].extend(n[j:j+len(s7[0])])
                        elif not s7[-1]:
                            s7[0].extend(n[j:j+len(s7[0])])
                        else:
                            ccd([n[j:j+len(s7[0])]],f,C[c])
            if s5 and (len(s7[0])>q or (s5 and s6)):
                temp=s7
                if c==1 and design:
                    temp.insert(0,[design]*len(s7[0]))
                ccd(temp,f,C[c])
                s7=[]
            for n in s4:
                temp=[]
                if sum(n)==1:
                    continue
                b=[s1[i] for i in range(len(n)) if n[i]==1]
                for m in b:
                    temp.append([x.replace('?',m) for x in s2 if s3[x]==list(n)])
                if s7 and a and a==[x[x.rfind('_'):] for x in temp[0][:len(s7[0])]]:
                    temp=s7+temp
                else:
                    ccd(s7,f,C[c])
                if c==1 and design:
                    temp.insert(0,[design]*len(temp[0]))
                ccd(temp,f,C[c])
    sfiles=[n for n in files if ('cleaned_aad.csv' in n or 'design_aad.csv' in n)]
    if len(sfiles)>1:
        f.write('### AMINO ACID ENRICHMENT ###\n')
        f.write('Instructions: Add Parent/Child pairs as needed, each Parent or Child group can have several members. Each member: prefix + tab + names of variable regions to be included separated by commas. Only positions in common by parent and child members will be used. If the same positions occur in more than one member, the first occurrence (file alphabetical order) will be used. Positions with a single amino acid in both groups will be omitted.\n')
        wcomp1([n for n in sfiles if 'design_aad.csv' in n],[n for n in sfiles if ('P_cleaned_aad.csv' in n or 'p_cleaned_aad.csv' in n)],f)
        wcomp1([n for n in sfiles if ('P_cleaned_aad.csv' in n or 'p_cleaned_aad.csv' in n)],[n for n in sfiles if ('V_cleaned_aad.csv' in n or 'v_cleaned_aad.csv' in n)],f)
        wcomp1([n for n in sfiles if ('V_cleaned_aad.csv' in n or 'v_cleaned_aad.csv' in n)],[n for n in sfiles if ('-1_cleaned_aad.csv' in n or '_1_cleaned_aad.csv' in n)],f)
        wcomp1([n for n in sfiles if ('-1_cleaned_aad.csv' in n or '_1_cleaned_aad.csv' in n)],[n for n in sfiles if ('-2_cleaned_aad.csv' in n or '_2_cleaned_aad.csv' in n)],f)
        wcomp1([n for n in sfiles if ('-2_cleaned_aad.csv' in n or '_2_cleaned_aad.csv' in n)],[n for n in sfiles if ('-3_cleaned_aad.csv' in n or '_3_cleaned_aad.csv' in n)],f)
        wcomp1([n for n in sfiles if ('-3_cleaned_aad.csv' in n or '_3_cleaned_aad.csv' in n)],[n for n in sfiles if ('-4_cleaned_aad.csv' in n or '_4_cleaned_aad.csv' in n)],f)
        f.write('\n\n')
    s=[n[:-15] for n in files if ('cleaned_md.csv' in n)]
    if s:
        f.write('### MUTANT POSITION DISTRIBUTION ###\n')
        f.write('Instructions: Each group surrounded by empty lines will be a separate chart. Data in same line (separated by blank space) will have different colors and will be grouped together.\n\n')
        s1=sorted(set([n[max(n.rfind('-')+1,n.rfind('_')+1):] for n in s]))
        s2=sorted(set([n[:max(n.rfind('-'),n.rfind('_'))] for n in s]))
        s3={}
        for x in s2:
            s3[x]=[]
            for n in s1:
                if x+'-'+n in s or x+'_'+n in s:
                    s3[x].append(1)
                else:
                    s3[x].append(0)
        s4=sorted(set([tuple(s3[n]) for n in s3]))
        for n in s4:
            if sum(n)==0:
                f.write('\n'.join([x for x in s if (x[:-1] in s3 and s3[x[:-1]]==list(n))])+'\n')
            if sum(n)==1:
                f.write('\n'.join([x for x in s if s3[x[:max(x.rfind('-'),x.rfind('_'))]]==list(n)])+'\n')
            if sum(n)>1:
                if s4.index(n)>0:
                    f.write('\n')
                for a in s2:
                    f.write(' '.join([x for x in s if (a==x[:max(x.rfind('-'),x.rfind('_'))] and s3[a][s1.index(x[max(x.rfind('-')+1,x.rfind('_')+1):])]==1)])+'\n')
                # print more than 1 name per line / include theoretical
                # Groups them like in aa enrichment!



            if s4.index(n)==len(s4)-1:
                f.write('\n')
    s=[n for n in files if (('_crude-' in n or '_cleaned' in n) and '.txt' in n)]
    if s:
        f.write('### SEQUENCE FREQUENCY EVOLUTION ###\n')
        f.write('Instructions: Each group surrounded by empty lines will be a separate chart. In each group: either min frequency in % or max number of variants (required, frequency if % sign present or float, number of sequences if integer), sequence name prefix (optional) and figure title (optional, will be created automatically if "auto") on first line (separated by space or tab), followed by data file names (required) and legend labels (optional, will be created automatically if absent, separated from file name by space or tab) in following lines in experimental chronological order (1 file per line).\n')
        s1=set([n[n.rfind('_crude-'):] for n in s if ('_crude-' in n and '.txt' in n and n[n.rfind('_crude-'):].count('-')==1)]+['_cleaned.txt' for n in s if '_cleaned.txt' in n])
        s1=sorted(s1)
        s5=[]
        for n in s1:
            s2=[k for k in s if n in k]
            s2.sort()
            if 'cleaned' in n:
                if [k for k in s if n in k and '_VR' in k]:
                    s3=set([k[:k.find('_VR')] for k in s2])
                    s6=sorted(set([k[k.find('_VR'):] for k in s2]))
                else:
                    s3=set([k[:k.rfind('_cleaned')] for k in s2])
                    s6=sorted(set([k[k.find('_cleaned'):] for k in s2]))
            else:
                s3=[k[:k.rfind('_crude-')] for k in s2]
                s6=sorted(set([k[k.find('_crude-'):] for k in s2]))
            s4=set([k[:-1] for k in s3])
            s4=sorted(s4)
            for m in s4:
                for p in s6:
                    if len([k for k in s3 if m in k])>1:
                        s5.append([])
                        for x in s2:
                            if m in x and p in x:
                                s5[-1].append(x)
        for i in range(len(s5)):
            f.write('\n25\tS\tauto\n')
            for x in s5[i]:
                f.write(x+'\n')
        f.write('\n')
        if lt=='undefined':
            f.write('### PARENTAL COVERAGE EVOLUTION ###\n')
            f.write('Instructions: Each group surrounded by empty lines will be a separate chart. In each group: data file names in experimental chronological order (1 file per line).\n')
            for i in range(len(s5)):
                if s5[i] and '_VR' in s5[i][0]:
                    continue
                f.write('\n')
                for x in s5[i]:
                    f.write(x+'\n')
            f.write('\n')
    f.close()
    print('\n  Edit the file caplib3_compare.txt before running caplib3 compare (without argument to process the edited file)!\n\n')

def ccd(data,f,lim):
    if not data or not data[0]:
        return
    p=0
    for j in range(len(data[-1])):
        if p>lim and data[-1][j][:data[-1][j].rfind('_')]!=data[-1][j-1][:data[-1][j-1].rfind('_')]:
            f.write('\n')
            p=0
        for i in range(len(data)):
            f.write(data[i][j%len(data[i])]+' ')
        f.write('\n')
        p+=1
    f.write('\n')

def compare2(format):
    if lt!='undefined':
        vrdic={}
        for n in vrlist:
            vrdic[n[0]]=n[1:]
        if not glob('compare_table.csv'):
            x=glob('*complexity.txt')
            if not x:
                print('\n  Library complexity file not found. Run caplib3 init to recreate it (with same arguments that were used for reads processing).\n')
                sys.exit()
            if len(x)>1:
                dbl.check_file('caplib3.conf',True)
                g=open('caplib3.conf','r')
                y=''
                for gline in g:
                    if gline[:11]=='# Library n':
                        y=True
                        continue
                    if y:
                        y=gline.strip()
                        y=y[:y.find('-')]
                        break
                x=[n for n in x if y in n and 'complexity.txt' in n]
                if len(x)!=1:
                    print('\n  More than one complexity file present in the current directory!\n')
                    sys.exit()
                g.close()
            x=x[0]
            complexity={}
            g=open(x,'r')
            vr=''
            frame=0
            for gline in g:
                gline=gline.strip()
                if vr and not gline and len(vrdic[vr])==5:
                    z=0
                    w=1
                    for n in p:
                        z+=1-n
                        w*=n
                    w=1-w
                    complexity[vr].append(z)
                    complexity[vr].append(w)
                    continue
                if gline[:14]=='Reading frame:':
                    frame=int(gline[-1])
                if gline[:13]=='Expected stop':
                    x=gline[31:-1]
                elif gline[:14]=='Expected amino':
                    y=gline[32:]
                    vr=''
                elif gline and gline[0].isdigit():
                    if not vr:
                        p=[]
                        i=0
                        z=int(gline.split()[0])*3+frame
                        vr=[n for n in vrdic if vrdic[n][0]==z]
                        if len(vr)!=1:
                            print('\n  Variable region not found in caplib3.conf!\n')
                            sys.exit()
                        vr=vr[0]
                        complexity[vr]=[x,y]
                    if len(vrdic[vr])<5:
                        continue
                    wt=vrdic[vr][-1][i]
                    i+=1
                    temp=gline.split()[5:]
                    temp2={}
                    for n in temp:
                        if n[0]!='*':
                            temp2[n[0]]=int(n[2:])
                    if wt in temp2:
                        p.append(temp2[wt]/sum(temp2.values()))
                    else:
                        p.append(0)
            g.close()
            table=[]
            g=open('compare_table.csv','w')
            g.write('Data prefix,VR name,VR size (aa),# variable positions,Expected % stop codons,Expected aa complexity,Reads,% unmapped reads,')
            g.write('% frameshifts,% stop codon,Extracted reads,Extracted aa complexity,Filtered reads,Filtered aa complexity,')
            g.write('Most common length (% reads),Most common sequence (% reads)')
            if len(vrlist[0])==6:
                g.write(',Expected mutations per read,Observed mutations per read,Expected % mutant,Observed % mutant\n')
            names=[n[:n.find('_extract_report.txt')] for n in glob('*_extract_report.txt')]
            if not names:
                print('  Extract report files missing!\n\n')
                sys.exit()
            for line in names:
                k=get_filtered(line)
                h=open(line+'_extract_report.txt','r')
                readfile=''
                vr=''
                i=-1
                j=[]
                for hline in h:
                    ln=hline.strip()
                    if not readfile:
                        if ln[:10]!='Read file:':
                            readfile=ln
                    elif ln[:16]=='Processed reads:':
                        reads=int(ln[17:])
                    elif ln[:16]=='Variable region:' or ln[:25]=='Combined variable regions':
                        vr=ln[ln.find('region')+8:]
                        i=0
                    elif i>-1 and ln:
                        i+=1
                        if '-' in vr and i==5:
                            i+=3
                        if i==7 and 'Next most common size' not in ln:
                            i+=1
                        if i in (1,2,3,4,10):
                            j.append(int(ln[ln.find(':')+2:]))
                    elif vr and j and not ln:
                        i=-1
                        temp=vr.split('-')
                        a=sum([len(vrdic[n][2])//3 for n in temp])
                        b=findvp(temp,vrdic)
                        for n in links:
                            if n[0]==readfile:
                                readfile=n[1]
                                break
                        c=[]
                        c.append(100*(1-(math.prod([1-float(complexity[n][0])/100 for n in temp]))))
                        c.append(math.prod([int(complexity[n][1]) for n in temp]))
                        c.append(round(sum([complexity[n][2] for n in temp if len(complexity[n])>2]),2))
                        c.append(round(100*(1-math.prod([1-complexity[n][3] for n in temp if len(complexity[n])>2])),2))
                        table.append([readfile,vr,str(a),str(b),str(c[0]),str(c[1]),str(reads),str(round((reads-j[0])/reads*100,2)),
                        str(round(j[1]/j[0]*100,2)),str(round(j[2]/(j[0]-j[1])*100,2)),str(j[3]),str(j[4]),
                        k[vr][0],k[vr][1],k[vr][2],k[vr][3]])
                        if len(vrlist[0])==6:
                            table[-1].extend([str(c[2]),k[vr][5],str(c[3]),k[vr][4]])
                        for n in table[-1]:
                            g.write(n+',')
                        g.write('\n')
                        j=[]
                h.close()
            g.close()
            print('\n  Table was saved into file: '+'compare_table.csv')
        else:
            table=[]
            g=open('compare_table.csv','r')
            for n in g:
                table.append(n.strip().split(','))
            del table[0]
            g.close()
    f=open('caplib3_compare.txt','r')
    if format:
        mppdf=''
    else:
        rename('compare_figs.pdf')
        fname='compare_figs.pdf'
        mppdf=PdfPages(fname)
    task=''
    for line in f:
        line=line.strip()
        if line[:17]=='### DATA CLEANING':
            task='Cleaning'
            s1=[]
            counter=0
            continue
        if line[:23]=='### CLUSTER CARDINALITY':
            task='Cardinality'
            s1=[]
            counter=0
            continue
        if line[:25]=='### AMINO ACID ENRICHMENT':
            task='Enrich'
            counter=0
            parent=None
            child=None
            continue
        if line[:22]=='### PROTEIN COMPLEXITY':
            task='Complexity'
            s1=[]
            counter=0
            continue
        if line[:32]=='### SEQUENCE FREQUENCY EVOLUTION':
            task='Evolution'
            s1=[]
            counter=0
            pre=''
            limit=23
            continue
        if line[:31]=='### PARENTAL COVERAGE EVOLUTION':
            task='Coverage'
            s1=[]
            counter=0
            continue
        if task=='Coverage':
            if (not line and not s1) or line[:13]=='Instructions:':
                continue
            if line:
                s1.append(line)
                continue
            cov={}
            for i in range(len(s1)):
                g=open(s1[i],'r')
                g.readline()
                total=0
                while True:
                    line=g.readline().strip().split('\t')
                    if not line or len(line)<2:
                        break
                    if not line[-1].isdigit():
                        line=line[:-1]
                    if not line[-1].isdigit():
                        print('\n  Wrong data file! Each sequence must be followed by its copy number!\n\n')
                        sys.exit()
                    n=int(line[-1])
                    line=line[0][1:-1].split('),(')
                    x=[k.split(',') for k in line]
                    if x[0][0].isdigit():
                        if len(x[-1])==4:
                            total+=n*(int(x[-1][0])+int(x[-1][3])-int(x[-1][2]))
                        else:
                            total+=n*(int(x[-1][0])+len(x[-1][1]))
                        for k in x:
                            if len(k)==4:
                                if not k[1] in cov:
                                    cov[k[1]]=[0]*len(s1)
                                cov[k[1]][i]+=(int(k[3])-int(k[2]))*n
                            else:
                                if not 'unmatched' in cov:
                                    cov['unmatched']=[0]*len(s1)
                                cov['unmatched'][i]+=n*len(k[1])
                    else:
                        total+=n*(sum([int(k[1]) for k in x]))
                        for k in x:
                            if not k[0] in cov:
                                cov[k[0]]=[0]*len(s1)
                            cov[k[0]][i]+=int(k[1])*n
                g.close()
                for n in cov:
                    cov[n][i]=cov[n][i]/total*100
            x=set([short(n[:n.rfind('.')]) for n in s1])
            if len(x)==1:
                gname=list(x)[0].replace('_cleaned','')
            else:
                gname='-'.join([short(n[:n.rfind('.')]) for n in s1]).replace('_cleaned','')
            z=gname+'-parental-coverage.csv'
            g=open(z,'w')
            x=[n[:n.rfind('_')] for n in s1]
            for n in x:
                g.write(','+n)
            g.write('\n')
            s2=sorted(cov,key=lambda x:max(cov[x]),reverse=True)
            for n in s2:
                g.write(n+','+','.join(list(map(str,cov[n])))+'\n')
            g.write('\n')
            g.close()
            print('  Parental coverage was saved into file: '+z+'\n')
            z='tab10'
            if len(cov)>10:
                z='tab20'
            colors,fig=dbl.plot_start(z,gname+' Parental coverage evolution')
            plt.ylabel('%')
            plt.stackplot(x,[cov[k] for k in s2],labels=s2,baseline='wiggle',colors=colors.colors,alpha=0.8)
            counter=dbl.plot_end(fig,counter,'parental_evolution-',format,mppdf)
            s1=[]
        if task=='Evolution':
            if (not line and not s1) or line[:13]=='Instructions:':
                continue
            if line and line.split()[0].replace('.','').replace('%','').isdigit():
                l=line.split()
                if '%' in l[0] or '.' in l[0]:
                    limit=float(l[0].replace('%',''))
                else:
                    limit=int(l[0])
                if len(l)>2:
                    pre=l[1]
                    title=l[2]
                elif len(l)==2:
                    if l[1][-1] in ('-','_') or len(l[1])<8:
                        pre=l[1]
                        title=''
                    else:
                        pre=''
                        title=l[1]
                else:
                    pre=''
                    title=''
                continue
            if line:
                x=line.split()
                if not 'cleaned.txt' in x[0]:
                    x[0]+='_cleaned.txt'
                s1.append(x)
                continue
            freqs={}
            for i in range(len(s1)):
                g=open(s1[i][0],'r')
                total=g.readline().strip()
                if total.isdigit():
                    total=int(total)
                else:
                    print('\n  Wrong data file! First line must contain total number of reads!\n\n')
                    sys.exit()
                while True:
                    line=g.readline().strip().split('\t')
                    if not line or len(line)<2:
                        break
                    if not line[-1].isdigit():
                        line=line[:-1]
                    if not line[-1].isdigit():
                        print('\n  Wrong data file! Each sequence must be followed by its copy number!\n\n')
                        sys.exit()
                    freq=int(line[-1])/total*100
                    if line[0] not in freqs:
                        freqs[line[0]]=[0]*len(s1)
                    freqs[line[0]][i]=freq
                g.close()
            temp=sorted(freqs,key=lambda x:max(freqs[x]),reverse=True)
            if isinstance(limit,int):
                s2=temp[:limit]
            else:
                s2=[]
                for n in temp:
                    if max(freqs[n])>=limit:
                        s2.append(n)
                    else:
                        break
            x=len(str(len(s2)))
            s3=[pre+('0'*(x-len(str(i))))+str(i) for i in range(1,len(s2)+1)]
            for i in range(len(s2)):
                x=s2[i].split('),(')
                if x[0][0]=='(' and len(x)==1 and x[0].count(',')==3:
                    x=x[0][1:-1].split(',')[1]
                    s3[i]=x



##### DEFINED LIBRARY -> find parent sequence (pp=parent aa file name -> do readfasta) and compare -> if = -> use parent name !!!







            d=s1[0][0][:s1[0][0].rfind('_')]
            c=d.rfind('_')
            if c!=-1:
                a=d[:c]
                b=d[c+1:]
                e='_('+b+')'
            else:
                a=d
                b=''
                e=''
            d=s1[-1][0][:s1[-1][0].rfind('_')]
            c=d[:d.rfind('_')]
            gname=a+'-'+c+e
            if title=='auto':
                title=a+' to '+c+e.replace('_',' ')+' Sequence frequency evolution'
            z=gname+'-sorted_sequences.txt'
            g=open(z,'w')
            for i in range(len(temp)):
                g.write(temp[i]+'\n')
            g.write('\n')
            g.close()
            print('  Sorted sequences were saved into file: '+z+'\n')
            x=[]
            for n in s1:
                if len(n)>1:
                    x.append(n[1])
                else:
                    break
            if len(x)!=len(s1):
                x=[n[0][:n[0].find('_')] for n in s1]
            s3.append('Other')
            freqs['Other']=[]
            for i in range(len(x)):
                freqs['Other'].append(100-sum([freqs[k][i] for k in s2]))
            z=gname+'-frequencies.csv'
            s2.append('Other')
            g=open(z,'w')
            g.write(','.join(x)+'\n')
            for i in range(len(temp)):
                g.write(','.join(list(map(str,freqs[temp[i]])))+'\n')
            g.write('\n')
            g.close()
            print('  Frequencies were saved into file: '+z+'\n')
            z=gname+'-selected_sequences.txt'
            g=open(z,'w')
            if lt=='undefined' or not pp:
                for i in range(len(s2)-1):
                    g.write(s3[i]+' '+temp[i]+'\n')
                g.write('\n')
            else:
                p=pp.replace('-aa','').replace('.fasta','')
                k=s1[0][0][:s1[0][0].rfind('_')]
                vrs=k[k.rfind('_')+1:].split('-')
                a=max(len(s3[0]),len(p))
                B=[]
                C=[]
                for vr in vrs:
                    C.append(str(vrdic[vr][0]//3+number))
                    B.append(max(len(vr),len(C[-1]),len(vrdic[vr][4])))
                g.write(' '*(a+2))
                for i in range(len(B)):
                    g.write(vrs[i]+' '*(B[i]+1-len(vrs[i])))
                g.write('\n'+' '*(a+2))
                for i in range(len(C)):
                    g.write(C[i]+' '*(B[i]+1-len(C[i])))
                g.write('\n'+' '*(a-len(p))+p+' ')
                for vr in vrs:
                    g.write(' '+vrdic[vr][4])
                for i in range(len(s2)-1):
                    g.write('\n'+' '*(a-len(s3[i]))+s3[i]+' ')
                    seq=s2[i].split(',')
                    l=''
                    for i in range(len(B)):
                        l+=' '
                        for j in range(len(seq[i])):
                            if j<len(vrdic[vrs[i]][4]) and seq[i][j]==vrdic[vrs[i]][4][j]:
                                l+='.'
                            else:
                                l+=seq[i][j]
                    g.write(l)
            g.write('\n\n')
            g.close()
            print('  Selected sequences were saved into file: '+z+'\n')
            z='tab10'
            if len(s2)>11:
                z='tab20'
            if title=='auto':
                title=gname+' Sequence frequency evolution'
            colors,fig=dbl.plot_start(z,title)
            if x[0].isdigit():
                plt.xlabel('Round of selection')
            plt.ylabel('%')
            plt.xlim(0,len(x)-1)
            plt.ylim(0,100)
            plt.stackplot(x,[freqs[k] for k in s2],labels=s3,colors=colors.colors[:len(s2)-1]+COLORS[:max(0,len(s2)-21)]+('whitesmoke',),alpha=0.8)
            counter=dbl.plot_end(fig,counter,'frequency_evolution-',format,mppdf)
            s1=[]
        if task=='Enrich':
            if line[:8]=='# Parent':
                parent={}
            elif line[:7]=='# Child':
                child={}
            elif line and parent!=None and child==None:
                l=line.split('\t')
                parent[l[0]]=l[-1].split(',')
            elif line and child!=None:
                l=line.split('\t')
                child[l[0]]=l[-1].split(',')
            if line or (not line and (parent==None or child==None)):
                continue
            if not parent or not child:
                parent=None
                child=None
                continue
            A=set()
            for n in parent:
                A.update(parent[n])
            B=set()
            for n in child:
                B.update(child[n])
            vrs=list(A&B)
            positions={}
            for n in vrs:
                for i in range(len(vrdic[n][2])//3):
                    positions[vrdic[n][0]//3+i+number]=n
            P={}
            for n in sorted(parent):
                x='_aad.csv'
                if not 'design' in n:
                    if dbl.check_file(n+'_cleaned'+x,False):
                        x='_cleaned'+x
                    elif not dbl.check_file(n+x,False):
                        print(' Failed to find amino acid distribution file for '+n+'!\n')
                        sys.exit()
                g=open(n+x,'r')
                for m in g:
                    l=m.split(',')
                    if l and l[0]:
                        l=[int(l[0])]+[float(x) for x in l[1:]]
                        if l[0] in positions and positions[l[0]] in parent[n] and l[0] not in P:
                            P[l[0]]=l[1:]
                g.close()
            C={}
            for n in sorted(child):
                x='_aad.csv'
                if not 'design' in n:
                    if dbl.check_file(n+'_cleaned'+x,False):
                        x='_cleaned'+x
                    elif not dbl.check_file(n+x,False):
                        print(' Failed to find amino acid distribution file for '+n+'!\n')
                        sys.exit()
                g=open(n+x,'r')
                for m in g:
                    l=m.split(',')
                    if l and l[0]:
                        l=[int(l[0])]+[float(x) for x in l[1:]]
                        if l[0] in positions and positions[l[0]] in child[n] and l[0] not in C:
                            C[l[0]]=l[1:]
                g.close()
            Pname='_'.join([n for n in sorted(parent)])
            Cname='_'.join([n for n in sorted(child)])
            parent=None
            child=None
            E=[]
            for n in sorted(positions):
                if n in P and n in C and (P[n].count(0)<19 or C[n].count(0)<19) and (max(P[n])<=0.995 or max(C[n])<=0.995):
                    x=[]
                    for i in range(20):
                        a=P[n][i]
                        b=C[n][i]
                        if P[n][i]<0.005:
                            a=0.005
                        if C[n][i]<0.005:
                            b=0.005
                        x.append(math.log10(b/a))
                    E.append(x)
                else:
                    del positions[n]
            if not positions:
                continue
            P1=[]
            C1=[]
            for n in sorted(positions):
                P1.append(P[n])
                C1.append(C[n])
            if format:
                counter+=1
                g='Amino_acid_enrichment-'+str(counter)+'.'+format
            else:
                g=mppdf
            enrichment(P1,C1,E,Pname,Cname,aa,sorted(positions),g)
            pos=sorted(positions)
            h=open(Pname+'__'+Cname+'_aae.csv','w')
            h.write(','+','.join(n for n in aa)+'\n')
            for i in range(len(pos)):
                h.write(str(pos[i])+','+','.join(str(n) for n in E[i])+'\n')
            h.close()
            print('  Amino acid enrichment table saved into file: '+Pname+'__'+Cname+'_aae.csv\n')
        if task=='Complexity':
            if (not line and not s1) or line[:13]=='Instructions:':
                continue
            if line:
                s1.append(line.split())
                continue
            cdata=[[0]*len(s1) for n in s1[0]]
            rdata=[[0]*len(s1) for n in s1[0]]
            for i in range(len(s1)):
                for j in range(len(s1[0])):   #i: line (samples, VRs) / j: column (Design / P / V 1...)
                    if '_design' in s1[i][j]:
                        a=s1[i][j+1][s1[i][j+1].rfind('_')+1:]
                        for x in table:
                            if x[1]==a:
                                break
                        else:
                            continue
                        if x[5].isdigit():
                            cdata[j][i]=int(x[5])
                        continue
                    a=s1[i][j][:s1[i][j].rfind('_')]
                    b=s1[i][j][s1[i][j].rfind('_')+1:]
                    for x in table:
                        if a==x[0] and x[1]==b:
                            break
                    else:
                        continue
                    cdata[j][i]=int(x[13])
                    rdata[j][i]=int(x[12])-int(x[13])
            if len(cdata)==1 and max(cdata[0])==0:
                s1=[]
                continue
            if len(s1[0])>1:
                xlabels=[short(n[-1]) for n in s1]
            else:
                xlabels=[n[-1] for n in s1]
            locs=list(range(len(s1)))
            lim=max([n+m for n,m in zip([x for y in cdata for x in y if '_design' not in s1[0][cdata.index(y)]],[x for y in rdata for x in y if '_design' not in s1[0][rdata.index(y)]])])*2
            for i in range(len(cdata)):
                for j in range(len(cdata[0])):
                    if cdata[i][j]>lim:
                        cdata[i][j]=lim
            colors,fig=dbl.plot_start('tab10','Protein complexity')
            z=0.94/len(s1[0])
            w=z*0.9
            for i in range(len(s1[0])):
                x=''
                if len(s1[0])>1:
                    x=label(s1[0][i])
                plt.bar([n+z*i for n in locs],cdata[i],width=w,color=colors.colors[i],label=x)
                plt.bar([n+z*i for n in locs],rdata[i],width=w,color='lightgrey',bottom=cdata[i])
            plt.xticks([n+z*i/2 for n in locs],xlabels,size=8,rotation=45)
            plt.yscale('log')
            plt.xlim(-0.25,len(s1))
            plt.ylim(1,lim)
            counter=dbl.plot_end(fig,counter,'protein_complexity-',format,mppdf)
            s1=[]
        if task=='Cardinality':
            if (not line and not s1) or line[:13]=='Instructions:':
                continue
            if line:
                s1.append(line.split())
                continue
            xdata=[]
            ydata=[]
            if len(set([len(k) for k in s1]))>1:
                print('\n  For cluster cardinality distribution, in each group, all lines must have same number of datasets!\n')
                sys.exit()
            for j in range(len(s1[0])):
                xdata.append({})
                ydata.append({})
                for i in range(len(s1)):
                    g=open(s1[i][j]+'_cleaned_cnd.csv','r')
                    temp=[x for x in table if s1[i][j]==x[0]+'_'+x[1]]
                    if temp:
                        temp=temp[0]
                    else:
                        continue
                    xdata[j][s1[i][j]]=[]
                    ydata[j][s1[i][j]]=[]
                    for m in g:
                        if m[0]=='C':
                            continue
                        m=m.split(',')
                        xdata[j][s1[i][j]].append(int(m[0]))
                        ydata[j][s1[i][j]].append(int(m[1])/int(temp[13]))
                    g.close()
            if not xdata or not xdata[0]:
                s1=[]
                continue
            markers=['o','P','X',(5,1),'D','s','^','v','>','>']
            colors,fig=dbl.plot_start('tab10','Sequence cluster cardinality distribution')
            for j in range(len(s1[0])):
                for i in range(len(s1)):
                    if s1[i][j] not in xdata[j]:
                        continue
                    plt.scatter(xdata[j][s1[i][j]],ydata[j][s1[i][j]],alpha=0.4,label=s1[i][j],marker=markers[j%10],color=colors.colors[i%10])
            plt.xscale('log')
            plt.yscale('log')
            plt.xlabel("Sequence cluster cardinality")
            plt.ylabel("Fraction of distinct sequences")
            counter=dbl.plot_end(fig,counter,'cluster_cardinality_distribution-',format,mppdf)
            s1=[]
        if task=='Cleaning':
            s2=['Clean reads','Reads failing clean-up','Reads with stop codon','Frame shifted reads','Unmapped reads',]
            if (not line and not s1) or line[:13]=='Instructions:':
                continue
            if line and not s1:
                s1=[[],[],[],[],[],[]]
            if line:
                for x in table:
                    if line[:line.rfind('_')]==x[0] and x[1]==line[line.rfind('_')+1:]:
                        break
                else:
                    continue
                a=int(x[6])-(int(x[6])*float(x[7])/100)
                b=a-(a*float(x[8])/100)
                s1[0].append(line)
                s1[1].append(int(x[12])/int(x[6])*100)
                s1[2].append((int(x[10])-int(x[12]))/int(x[6])*100)
                s1[3].append(b*float(x[9])/int(x[6]))
                s1[4].append(a*float(x[8])/int(x[6]))
                s1[5].append(float(x[7]))
                continue
            colors,fig=dbl.plot_start('tab10','Data cleaning')
            for i in range(5):
                if i:
                    bottom=[n+m for n,m in zip(bottom,s1[i])]
                else:
                    bottom=[0]*len(s1[0])
                plt.bar(s1[0],s1[i+1],color=colors.colors[i],bottom=bottom,label=s2[i])
            plt.xticks(s1[0],size=8,rotation=45)
            plt.xlim(-1,len(s1[0]))
            plt.ylim(0,100)
            plt.ylabel('% total reads')
            counter=dbl.plot_end(fig,counter,'data_cleaning-',format,mppdf)
            s1=[]
    if not format:
        mppdf.close()
        print('  All figures were saved into single multipage file: '+fname)
    f.close()
    print()

def findvp(L,vrdic):
    b=0
    for l in L:
        for n in range(len(vrdic[l][2])//3):
            for m in vrdic[l][2][n*3:n*3+3]:
                if m in ambiguous:
                    b+=1
                    break
    return b

def short(x):
    b=x[x.rfind('_'):]
    a=x[:x.rfind('_')]
    c=a.find('_')
    if c>-1:
        a=a[:c]
    return a+b

def label(x):
    if '_design' in x:
        return 'Design'
    a=x[:x.rfind('_')]
    if '_' not in a and '-' not in a:
        return a
    return a[max(a.rfind('_'),a.rfind('-'))+1:]

def select(args):
    fname='caplib3_select.txt'
    if args.select_file:
        fname=args.select_file
        dbl.check_file(fname,True)
    format=dbl.check_plot_format(args.file_format)
    if args.new:
        rename('caplib3_select.txt')
    if glob(fname):
        f=open(fname,'r')
        read=''
        combi=[]
        thr=-1
        tsc=0
        msc=0
        print()
        for line in f:
            ln=line.strip()
            if ln[:8]=='# PARENT':
                read='parent'
                pre=''
                path=''
                parent=''
                child=''
            if ln[:11]=='# THRESHOLD':
                read='thr'
            if ln[:12]=='# TOP SCORES':
                read='tsc'
            if ln[:15]=='# MINIMUM SCORE':
                read='msc'
            if not ln or ln[0]=='#' or ln[:13]=='Instructions:':
                continue
            if read=='parent':
                if not pre:
                    pre=ln
                    continue
                if not path:
                    path=ln
                    continue
                if not parent:
                    parent=ln.split()
                    continue
                if not child:
                    child=ln.split()
                combi.append((pre,path,parent,child))
                pre=''
                path=''
                parent=''
                child=''
                continue
            if read=='thr':
                if thr>0:
                    print('  A single threshold value should be entered in the THRESHOLD section!\n')
                    sys.exit()
                if not ln.replace('.','').replace('-','').isdigit() or (not 0<=float(ln)<100 and ln!='-1' ):
                    print('  A number between -1 and 100 should be entered in the THRESHOLD section!\n')
                    sys.exit()
                if ln=='-1':
                    thr=int(ln)
                else:
                    thr=float(ln)
            if read=='tsc':
                if tsc:
                    print('  A single value should be entered in the TOP SCORES section!\n')
                    sys.exit()
                if not ln.isdigit():
                    print('  An integer value should be entered in the TOP SCORES section!\n')
                    sys.exit()
                tsc=int(ln)
            elif read=='msc':
                if msc:
                    print('  A single minimum score value should be entered in the MINIMUM SCORE section!\n')
                    sys.exit()
                if not ln.replace('.','').isdigit():
                    print('  A number >=0 should be entered in the MINIMUM SCORE section!\n')
                    sys.exit()
                msc=float(ln)
        if not combi:
            print('  Parent/child combinations are missing!n')
            sys.exit()
        for pre,path,parent,child in combi:
            z=''
            if '\\' in path:
                z='\\'
            elif '/' in path:
                z='/'
            if z and path[-1]!=z:
                path+=z
            if not glob(path+parent[0]+'*'):
                print('  Wrong path or wrong file name '+path+parent[0]+' !\n')
                sys.exit()
            parent=[parent]
            if not format:
                sname='select-'+pre+str(thr)+'_figs.pdf'
                mppdf=PdfPages(sname)
            seqs={}
            for n in range(len(child)):
                x=glob(child[n]+'*cleaned.txt')
                if not x:
                    x=glob(child[n]+'*.txt')
                    if not x:
                        x=glob(child[n])
                        if not x:
                            print('  No relevant file found for '+child[n]+'!\n')
                            sys.exit()
                if len(x)>1:
                    x=[i for i in x if 'report.txt' not in i]
                    if len(x)>1:
                        x=[i for i in x if len(i)==max(len(j) for j in x)]
                        if len(x)>1:
                            x=[i for i in x if ('all' in i or 'All' in i)]
                if not x or len(x)>1:
                    print('  No unambiguous file search result for '+child[n]+'!\n')
                    sys.exit()
                x=x[0]
                y=child[n].replace('_cleaned.txt','')
                child[n]=(y,x)
            x=[(n[0][:max(n[0].rfind('_'),len(n[0]))],n[1]) for n in child]
            if len(set(k for k,_ in x))==len(x):
                child=list(x)
            for i in range(len(child)):
                g=open(child[i][1],'r')
                N=int(g.readline().strip())
                for ln in g:
                    l=ln.strip().split()
                    x=int(l[1])/N*100
                    if (thr>-1 and x<thr) or (thr==-1 and int(l[1])==1):
                        break
                    if l[0] not in seqs:
                        seqs[l[0]]=[0]*len(child)
                    seqs[l[0]][i]=x
                g.close()
            if not seqs:
                print('  No sequence found. Please decrease the threshold!\n')
                sys.exit()
            x=int(math.log10(len(seqs)))+1
            y=sorted(seqs,key=lambda k:max(seqs[k]),reverse=True)
            sn={}
            i=0
            for n in y:
                i+=1
                a=str(i)
                sn[pre+'0'*(x-len(a))+a]=n
            fname='select-'+pre+str(thr)+'_sequences.fasta'
            f=open(fname,'w')
            f.write('\n'.join('>'+x+'\n'+sn[x] for x in sn)+'\n')
            f.close()
            print('  Selected sequences were saved into file: '+fname+'\n')
            vrlist,links,number,pp,lt=readinit('extract')
            if lt!='undefined' and not vrlist:
                print('  List of variable regions not found in caplib3.conf !\n')
                sys.exit()
            vrdic={}
            for n in vrlist:
                vrdic[n[0]]=n[1:]
            vrs=[]
            for n in links:
                if n[1]==child[0][0]:
                    vrs=[[x] for x in n[-1]]
                    break
            if not vrs:
                vrs=[[n[0]] for n in vrlist]
            for i in range(len(vrs)):
                vrs[i].append(vrdic[vrs[i][0]][0]//3+number)
                vrs[i].append(vrdic[vrs[i][0]][4])
            k=child[0][1]
            Y=k[k[:k.rfind('_')].rfind('_')+1:k.rfind('_')].split('-')
            if lt!='undefined':
                seqformat(fname,pp,[k for k in vrs if k[0] in Y])
            fname='select-'+pre+str(thr)+'_frequencies.csv'
            f=open(fname,'w')
            f.write(','+','.join([n[0] for n in child])+'\n')
            f.write('\n'.join([n+','+','.join([str(m) for m in seqs[sn[n]]]) for n in sorted(sn)]))
            f.write('\nOther,'+','.join([str(100-sum([seqs[n][i] for n in seqs])) for i in range(len(child))])+'\n')
            f.close()
            print('  Frequencies of selected sequences were saved into file: '+fname+'\n')
            ratio=[1]
            if dbl.check_file(path+'caplib3_mix.txt',False):
                input,x,output=readmix(path)
                if len(parent[0])==1 and parent[0][0]==output:
                    parent=list(input)
                    ratio=x
            for n in range(len(parent)):
                for m in range(len(parent[n])):
                    x=glob(path+parent[n][m]+'*')
                    if len(x)>1:
                        x=glob(path+parent[n][m]+'*.txt')
                        if len(x)>1:
                            x=glob(path+parent[n][m]+'*_cleaned.txt')
                            if len(x)>1:
                                x=[i for i in x if len(i)==max(len(j) for j in x)]
                                if len(x)>1:
                                    x=[i for i in x if ('all' in i or 'All' in i)]
                    if not x or len(x)>1:
                        print('  Parent '+parent[n][m]+' not found or ambiguous search result!\n')
                        sys.exit()
                    x=x[0]
                    parent[n][m]=x
            parts=[[set(k[k[:k.rfind('_')].rfind('_')+1:k.rfind('_')].split('-')) for k in l] for l in parent]
            X=[]
            [X.append(k) for m in parts for l in m for k in l if k not in X]
            if all(k in X for k in Y):
                V=set(list((Y)))
            elif X!=Y and all(k in Y for k in X):
                print("  Warning! Some variable regions of child sequences don't exist in parent sequences. Enrichment scores can only be calculated for shared regions.\n")
                V=set([k for k in Y if k in X])
            elif lt!='undefined':
                print('  Variable regions of parent and child sequences do not match!\n')
                sys.exit()





    ########################################  CHANGE !!!!!!!!!!!!!!!!!!!!!

            if lt=='undefined':
                V=set(['BL2'])
    #############################################################


            P=[]
            temp=[k&V for n in parts for k in n if len(k&V)>1]
            temp.sort(key=len,reverse=True)
            for n in temp:
                p2=[n]
                while p2:
                    p2.sort(key=len)
                    p=p2[-1]
                    p2.remove(p)
                    for x in P:
                        if p<=x:
                            break
                    if P and x and p<=x:
                        continue
                    for m in parts:
                        c=0
                        t=[]
                        for l in m:
                            if p<=l:
                                break
                            l1=l&p
                            if l1 and l1<p:
                                c+=1
                                t.append(l1)
                        if c<2 or p<=l:
                            continue
                        left=p-set([k for k1 in t for k in k1])
                        if not left:
                            [p2.append(k) for k in t if len(k)>1]
                        else:
                            [p2.append(k|left) for k in t]
                        break
                    else:
                        for x in P:
                            if x<=p:
                                P.remove(x)
                                break
                        P.append(p)
            P+=[set([k]) for k in V if k not in [x for y in P for x in y]]
            for n in sn:
                sn[n]=sn[n].split(',')
            plots=1
            if len(P)==1 and len(P[0])==1:
                plots-=1
            if glob('*aae.csv'):
                plots+=1
            plot=1
            Sscore={}
            Vscore={}
            Ascore={}
            if (P and max([len(k) for k in P])>1) or len(P)<2:
                plots+=1
                cfreq=[{tuple(s[Y.index(m)] for m in [k for k in Y if k in n]):[] for s in sn.values()} for n in P]
                for n in child:
                    for i in range(len(P)):
                        dic,total=f2dl(n[1],Y,[k for k in Y if k in P[i]])
                        for s in cfreq[i]:
                            cfreq[i][s].append(dic[s]/total)
                pfreq=[{tuple(s[Y.index(m)] for m in [k for k in Y if k in n]):[] for s in sn.values()} for n in P]
                for i in range(len(parent)):
                    for p in range(len(P)):
                        fl=[]
                        wl=[k for k in Y if k in P[p]]
                        wl2=[k[2] for k in vrs if k[0] in wl]
                        total=1
                        for j in range(len(parent[i])):
                            for n in parts[i][j]:
                                if n in P[p]:
                                    wl.remove(n)
                                    fl.append(n)
                            if fl:
                                A=[k for k in Y if k in parts[i][j]]
                                B=[k for k in Y if k in fl]
                                dic,total=f2dl(parent[i][j],A,B)
                                break
                        I=[A.index(m) for m in B]
                        for s in pfreq[p]:
                            if wl and len([k for k in wl2 if k in s])<len(wl):
                                q=0
                            elif not fl and tuple(wl2)==s:
                                q=1
                            else:
                                z=tuple(s[k] for k in I)
                                q=max(0.5,dic[z])
                            pfreq[p][s].append(q/total)
                for n in sorted(sn):
                    Sscore[n]=[]
                    for i in range(len(child)):
                        q=1
                        for j in range(len(P)):
                            s=tuple(sn[n][k] for k in [Y.index(x) for x in Y if x in P[j]])
                            q*=max(0.1,cfreq[j][s][i]/sum([ratio[k]*(pfreq[j][s][k]) for k in range(len(ratio))]))
                        Sscore[n].append(math.log10(q)/len(P))
                fname='select-'+pre+str(thr)+'_ses.csv'
                f=open(fname,'w')
                f.write(','+','.join(n[0] for n in child)+'\n')
                f.write('\n'.join([n+','+','.join([str(m) for m in Sscore[n]]) for n in sorted(Sscore)]))
                f.close()
                print('  Sequence enrichment scores were saved into file: '+fname+'\n')
                fig=plt.figure(figsize=(12,6.75))
                heatmap(fig,plots,plot,'Sequence enrichment',[Sscore[n] for n in sorted(Sscore)],[n[0] for n in child],sorted(sn))
                plot+=1
            if lt!='undefined' and (len(P)!=1 or len(P[0])!=1):
                V=[k for k in Y if k in V]
                cfreq=[{s[Y.index(m)]:[] for s in sn.values()} for m in V]
                for vr in V:
                    for c in child:
                        dic,total=f2dl(c[0]+'_'+vr+'_cleaned.txt','','')
                        for s in cfreq[V.index(vr)]:
                            a=0
                            if s in dic:
                                a=dic[s]
                            cfreq[V.index(vr)][s].append(a/total)
                pfreq=[{s[Y.index(m)]:[] for s in sn.values()} for m in V]
                for i in range(len(parent)):
                    P=[k for k in V for m in parts[i] for n in m if k in n]
                    for vr in V:
                        if vr in P:
                            x=parent[i][parts[i].index([k for k in parts[i] if vr in k][0])]
                            x=x[:x.rfind('_')][:x[:x.rfind('_')].rfind('_')]
                            dic,total=f2dl(x+'_'+vr+'_cleaned.txt','','')
                        else:
                            dic,total={[k[2] for k in vrs if k[0]==vr][0]:1},1
                        for s in pfreq[V.index(vr)]:
                            a=0
                            if vr in P:
                                a=0.5
                            if s in dic:
                                a=dic[s]
                            pfreq[V.index(vr)][s].append(a/total)
                E=[{} for n in V]
                for n in sorted(sn):
                    Vscore[n]=[]
                    for i in range(len(child)):
                        q=1
                        for j in range(len(V)):
                            s=sn[n][Y.index(V[j])]
                            h=max(0.1,cfreq[j][s][i]/sum([ratio[k]*(pfreq[j][s][k]) for k in range(len(ratio))]))
                            if s not in E[j]:
                                E[j][s]=[0]*len(child)
                            if not E[j][s][i]:
                                E[j][s][i]=h
                            q*=h
                        Vscore[n].append(math.log10(q)/len(V))
                fname='select-'+pre+str(thr)+'_vres.csv'
                f=open(fname,'w')
                f.write(','+','.join(n[0] for n in child)+'\n')
                f.write('\n'.join([n+','+','.join([str(m) for m in Vscore[n]]) for n in sorted(Vscore)]))
                f.close()
                print('  Variable region enrichment scores were saved into file: '+fname+'\n')
                heatmap(fig,plots,plot,'VR enrichment',[Vscore[n] for n in sorted(Vscore)],[n[0] for n in child],sorted(sn))
                plot+=1
            aae=[]
            aaef=glob('*aae.csv')
            if aaef:
                for n in child:
                    x=[k for k in aaef if (n[0]+'_aae.csv' in k)]
                    if len(x)!=1:
                        print('  Warning! amino acid enrichment file could not be found for '+n[0]+' !\n')
                        continue
                    aae.append({})
                    f=open(x[0],'r')
                    for m in f:
                        if m[0]==',':
                            continue
                        m=m.strip().split(',')
                        aae[-1][m[0]]=m[1:]
                if not aae:
                    return
                b=findvp(V,vrdic)
                for n in sorted(sn):
                    Ascore[n]=[0]*len(child)
                    x=sn[n]
                    for i in range(len(x)):
                        ind=[k for k in range(len(vrs)) if Y[i] in vrs[k]][0]
                        for j in range(len(x[i])):
                            q=str(vrs[ind][1]+j)
                            for k in range(len(aae)):
                                if q in aae[k]:
                                    Ascore[n][k]+=float(aae[k][q][aa.index(x[i][j])])/b
                fname='select-'+pre+str(thr)+'_aaes.csv'
                f=open(fname,'w')
                f.write(','+','.join(n[0] for n in child)+'\n')
                f.write('\n'.join([n+','+','.join([str(m) for m in Ascore[n]]) for n in sorted(Ascore)]))
                f.close()
                print('  Amino acid enrichment scores were saved into file: '+fname+'\n')
                heatmap(fig,plots,plot,'Amino acid enrichment',[Ascore[n] for n in sorted(Ascore)],[n[0] for n in child],sorted(sn))
            fig.tight_layout()
            if format:
                g='select_fig-ES_'+pre+str(thr)+'.'+format
                plt.savefig(g,dpi=600)
                print('  Figure was saved into file: '+g+'\n')
            else:
                mppdf.savefig()
            plt.close()
            aaselec=[]
            for j in range(len(Y)):
                a=[sn[k][j] for k in sn]
                aaselec.append([])
                ind=[k for k in range(len(vrs)) if Y[j] in vrs[k]][0]
                for k in range(len(vrs[ind][2])):
                    aaselec[-1].append(set([l[k] for l in a if len(l)>k]))
            f=open('select-'+pre+str(thr)+'_top_scores.html','w')
            f.write('<html>\n<head></head>\n<body><p><pre>\n')
            if '.' in pp:
                pp=pp[:max(0,pp.rfind('-'))]
            Cscore={}
            for n in sorted(sn):
                Cscore[n]=[]
                for i in range(len(child)):
                    x=0
                    if Sscore:
                        x+=Sscore[n][i]
                    if Vscore:
                        x+=Vscore[n][i]
                    if Ascore:
                        x+=Ascore[n][i]
                    Cscore[n].append(x)
            Opt_seq=[]
            Opt_score=[]
            for i in range(len(child)):
                Opt_seq.append({})
                Opt_score.append({})
                if Vscore:
                    q=1
                    l=''
                    for n in E:
                        a=list(n.keys())
                        b=[c[i] for c in list(n.values())]
                        k=a[b.index(max(b))]
                        q*=n[k][i]
                        l+=k+','
                    l=l[:-1]
                    q=math.log10(q)/len(V)
                    Opt_seq[-1]['Opt-VR']=l
                    Opt_score[-1]['Opt-VR']=[]
                    k=0
                    l=l.split(',')
                    if l in sn.values() and Sscore:
                        x=[n for n,m in sn.items() if m==l][0]
                        k=Sscore[x][i]
                    if Sscore:
                        Opt_score[-1]['Opt-VR'].append(k)
                    Opt_score[-1]['Opt-VR'].append(q)
                    r=0
                    if Ascore:
                        vp=findvp(V,vrdic)
                        for a in range(len(l)):
                            ind=[k for k in range(len(vrs)) if Y[a] in vrs[k]][0]
                            for b in range(len(l[a])):
                                p=str(vrs[ind][1]+b)
                                if p in aae[i]:
                                    r+=float(aae[i][p][aa.index(l[a][b])])/vp
                        Opt_score[-1]['Opt-VR'].append(r)
                if Ascore:
                    l=''
                    q=0
                    vp=findvp(V,vrdic)
                    for v in range(len(Y)):
                        ind=[k for k in range(len(vrs)) if Y[v] in vrs[k]][0]
                        for j in range(len(vrs[ind][2])):
                            a=str(j+vrs[ind][1])
                            if a in aae[i]:
                                b=sorted([float(k) for k in aae[i][a]],reverse=True)
                                for n in range(20):
                                    c=aa[[float(k) for k in aae[i][a]].index(b[n])]
                                    if c in aaselec[v][j]:
                                        l+=c
                                        q+=b[n]/vp
                                        break
                            else:
                                l+=vrs[ind][2][j]
                        l+=','
                    l=l[:-1]
                    Opt_seq[-1]['Opt-aa']=l
                    Opt_score[-1]['Opt-aa']=[]
                    k=0
                    l=l.split(',')
                    if l in sn.values() and Sscore:
                        x=[n for n,m in sn.items() if m==l][0]
                        k=Sscore[x][i]
                    if Sscore:
                        Opt_score[-1]['Opt-aa'].append(k)
                    if Vscore:
                        r=1
                        for a in range(len(l)):
                            if l[a] in E[a]:
                                r*=E[a][l[a]][i]
                        r=math.log10(r)/len(V)
                        Opt_score[-1]['Opt-aa'].append(r)
                    Opt_score[-1]['Opt-aa'].append(q)
            for i in range(len(child)):
                A=max(len(pp),max(len(k) for k in sn),6)+2
                map=[(0.001,'#e60000'),(0.01,'#ff6666'),(0.1,'#ffb3b3'),(0.8,'#ffe6e6'),(2,'#ffffff'),(10,'#e6e6ff'),(100,'#b3b3ff'),(1000,'#6666ff'),'#0000e6']
                f.write('\n</pre><font face = "Sans-serif" size = "5"><b>'+child[i][0]+'</b></font><pre>\n')
                f.write(' '*(A+1))
                b=[]
                for k in range(len(Y)):
                    ind=[z for z in range(len(vrs)) if Y[k] in vrs[z]][0]
                    b.append(max(len(vrs[ind][0]),len(str(vrs[ind][1])),len(vrs[ind][2])))
                    f.write(' <b>'+vrs[ind][0]+' </b>'*(b[k]-len(vrs[ind][0])))
                f.write('\n'+' '*(A+1))
                for k in range(len(Y)):
                    ind=[z for z in range(len(vrs)) if Y[k] in vrs[z]][0]
                    f.write(' '+str(vrs[ind][1])+' '*(b[k]-len(str(vrs[ind][1]))))
                f.write('\n'+' '*(A-len(pp))+pp+' ')
                for k in range(len(Y)):
                    ind=[z for z in range(len(vrs)) if Y[k] in vrs[z]][0]
                    a=vrs[ind][2]
                    for j in range(len(a)):
                        c=str(j+vrs[ind][1])
                        if Ascore and c in aae[i]:
                            r=float(aae[i][c][aa.index(vrs[ind][2][j])])
                            if r>=1:
                                a='<u><b>'+a+'</b></u>'
                            elif r>=0.1:
                                a='<u>'+a+'</u>'
                    if Vscore and vrs[ind][2] in E[k]:
                            c=cmap(E[k][vrs[ind][2]][i],map)
                            a='<span style="background-color: '+c+'">'+a+'</span>'
                    f.write(' '+a+' '*(b[k]-len(vrs[ind][2])))
                x=''
                y=''
                z=''
                if Sscore:
                    x='S-score'
                if Vscore:
                    y=' V-score'
                if Ascore:
                    z=' A-score'
                f.write(' <b>  %    '+x+y+z+'   Total')
                x=[child[j][0] for j in range(len(child)) if j!=i]
                if len(x)>1:
                    while True:
                        if len(set([k[0] for k in x]))!=1 or len([k for k in x if len(k)==1]):
                            break
                        x=[k[1:] for k in x]
                z=5
                if x:
                    z=max(5,max([len(k) for k in x]))
                x=''.join([' '*(1+z-len(k))+k for k in x])
                f.write(' '+x+'</b>\n')
                temp=sorted([k for k in Cscore if Cscore[k][i]>=msc],key=lambda x:Cscore[x][i],reverse=True)[:tsc]+[k for k in Opt_score[i]]
                for n in temp:
                    if n[:4]=='Opt-':
                        l=' '*(A-len(n))+'<em>'+n+'</em> '
                        s=Opt_seq[i][n].split(',')
                    else:
                        l=' '*(A-len(n))+n+' '
                        s=sn[n]
                    for k in range(len(Y)):
                        ind=[z for z in range(len(vrs)) if Y[k] in vrs[z]][0]
                        m=' '
                        for j in range(len(vrs[ind][2])):
                            if j>=len(s[k]):
                                m+='-'
                            elif s[k][j]==vrs[ind][2][j]:
                                m+='.'
                            else:
                                c=s[k][j]
                                a=str(j+vrs[ind][1])
                                if Ascore and a in aae[i]:
                                    r=float(aae[i][a][aa.index(s[k][j])])
                                    if r>=1:
                                        c='<u><b>'+c+'</b></u>'
                                    elif r>=0.1:
                                        c='<u>'+c+'</u>'
                                m+=c
                        if Vscore and s[k] in E[k]:
                            c=cmap(E[k][s[k]][i],map)
                            m=' <span style="background-color: '+c+'">'+m[1:]+'</span>'
                        l+=m+' '*(b[k]-len(vrs[ind][2]))
                    if n[:4]=='Opt-':
                        y='      <em>'
                        z='</em>'
                        x=Opt_score[i][n]
                    else:
                        z=''
                        y="{0:6.2f}".format(seqs[','.join(sn[n])][i])
                        x=[]
                        if Sscore:
                            x.append(Sscore[n][i])
                        if Vscore:
                            x.append(Vscore[n][i])
                        if Ascore:
                            x.append(Ascore[n][i])
                        x.append(Cscore[n][i])
                    x=''.join(["{0:8.2f}".format(k) for k in x])
                    if n[:4]=='Opt-':
                        w=''
                    else:
                        w=[Cscore[n][j] for j in range(len(child)) if j!=i]
                        c=''
                        if w:
                            c=cmap(Cscore[n][i]/max(0.001,max(w)),[(2,'#ffffff'),(5,'#e6ffe6'),(10,'#99ff99'),'#00e600'])
                        w=' <span style="background-color: '+c+'">'+''.join(["{0:6.2f}".format(k) for k in w])+'</span>'
                    f.write(l+' '+y+x+z+w+'\n')
            f.write('<br><br></pre></p></body></html>\n\n')
            f.close()
            print('  Sequences with top enrichment scores were saved into file: select-'+pre+str(thr)+'_top_scores.html'+'\n')
            Gscores=[]
            for i in range(len(child)):
                Gscores.append([])
                x=[Cscore[k][i] for k in Cscore if Cscore[k][i]>=msc]
                total=sum(x)
                Gscores[-1].append(max(x))
                Gscores[-1].append(total)
                matrix=[]


    ################# CREATE ALIGNMENT IN CASE OF VARIABLE LENGTHS ! ##############################################################




                x=[(''.join(sn[k]),Cscore[k][i]) for k in Cscore if Cscore[k][i]>=msc]
                z=Counter([len(k[0]) for k in x])
                ln=max(z,key=z.get)
                for j in range(ln):
                    matrix.append([])
                    y=defaultdict(int)
                    for n in x:
                        if len(n[0])!=ln:
                            continue
                        y[n[0][j]]+=n[1]
                    for a in aa:
                        z=0
                        if a in y:
                            z=y[a]/total
                        matrix[-1].append(z)
                Gscores[-1].append(dbl.entropy(matrix))
            colors,fig=dbl.plot_start('tab10','Global enrichment')
            sf=10000/max([k[1] for k in Gscores])
            plt.scatter(x=[k[0] for k in child],y=[k[0] for k in Gscores],s=[k[1]*sf for k in Gscores],c=[k[2] for k in Gscores],alpha=0.6)
            plt.ylabel("Max enrichment score")
            plt.colorbar(label='Enrichment entropy')
            plt.xticks(rotation=90)
            c
            fig.tight_layout()
            if format:
                g='global_enrichment_'+pre+str(thr)+'.'+format
                plt.savefig(g,dpi=600)
                print('  Figure was saved into file: '+g+'\n')
            else:
                mppdf.savefig()
            plt.close()
            if not format:
                mppdf.close()
                print('  Figures were saved into file: '+sname+'\n')
        return
    f=open('caplib3_select.txt','w')


    #  DETECT POSSIBLE ENTRIES
# check if caplib3_mix.txt exists, then copy output prefix from it and use it as the parent prefix


    x=glob('*_cleaned.txt')
    x=[k[:k.rfind('_')] for k in x]
    if '_' in x[0]:
        x=[k[:k.rfind('_')] for k in x]
    y=sorted(set([k[-1] for k in x]))
    combi=[]
    if len(y)>1:
        z=sorted(set([k[:-1] for k in x]))
        for n in z:
            for i in range(len(y)-1):
                if n+y[i] in x and n+y[i+1] in x:
                    combi.append((n,n+y[i],n+y[i+1]))
    f.write('# PARENT/CHILD COMBINATIONS\nInstructions: add combinations below, separated by empty lines. Each combination must have 4 lines:\n')
    f.write('  # Sequence prefix: sequences will be named using the sequence prefix followed by a number.\n')
    f.write('  # Path to parent file(s): if parent files are not in the current directory, write the path to access them, otherwise write "./" (child files must be in current directory).\n')
    f.write('  # Parent(s): write name(s) of file(s) containing parental sequences (prefix only is OK), separated by space or tab. Multiple files must be from the same library (to cover the length of the child sequences). If the parent is a mix of more than one library, instead of entering a file name, enter the same prefix that was entered in the # OUTPUT section of caplib3_mix.txt (run the mix program if necessary).\n')
    f.write('  # Child(ren): write name(s) of file(s) containing child sequences (prefix only is OK), separated by space or tab, in the order you want them to appear when results are displayed.\n\n')
    for n in combi:
        f.write(n[0]+'\n./\n'+n[1]+'\n'+n[2]+'\n\n')
    f.write('# THRESHOLD\nInstructions: sequences with frequency equal or higher to the threshold, expressed in %, will be selected for enrichment analysis. If no number is entered (or the number -1), all sequences present in more than one copy will be used.\n\n-1\n\n')
    f.write('# TOP SCORES\nInstructions: number of top scores to be displayed in the top score file.\n\n25\n\n')
    f.write('# MINIMUM SCORE\nInstructions: sequences with global enrichment score equal or higher to the minimum score will be used in calculations (recommended value: between 0 and 1).\n\n0.1\n\n')
    f.write('##### END OF CONFIGURATION FILE ##### ')
    f.close()
    print('\n  Edit the file caplib3_select.txt before running caplib3 select again!\n\n')

def seqformat(fname,pp,vrs):
    if '.' in pp:
        pp=pp[:max(0,pp.rfind('-'))]
    f=open(fname,'r')
    seq=[]
    a=True
    while a:
        a=f.readline().strip()
        b=f.readline().strip().split(',')
        if a and b:
            seq.append([a[1:]]+b)
    f.close()
    if len(seq[0])-1!=len(vrs):
        print('  Mismatch in number of variable regions!\n')
        sys.exit()
    for i in range(len(vrs)):
        x=set([len(x[i+1]) for x in seq])
        if len(x)>1 or next(iter(x))!=len(vrs[i][2]):
            print('  Warning! '+fname+' contains a sequence with different length\n')
            #######################################################################



            ############## Make alignment!!!!!!!!!!!!
    fname=fname.replace('.fasta','.txt')
    f=open(fname,'w')
    a=max(len(pp),len(seq[0][0]))+2
    c=a-len(seq[0][0])
    f.write(' '*(a+1))
    b=[]
    for i in range(len(vrs)):
        b.append(max(len(vrs[i][0]),len(str(vrs[i][1])),len(vrs[i][2])))
        f.write(' '+vrs[i][0]+' '*(b[i]-len(vrs[i][0])))
    f.write('\n'+' '*(a+1))
    for i in range(len(vrs)):
        f.write(' '+str(vrs[i][1])+' '*(b[i]-len(str(vrs[i][1]))))
    f.write('\n'+' '*(a-len(pp))+pp+' ')
    for i in range(len(vrs)):
        f.write(' '+vrs[i][2]+' '*(b[i]-len(vrs[i][2])))
    f.write('\n')
    for n in seq:
        l=' '*(c)+n[0]+' '
        for i in range(len(vrs)):
            if len(n[i+1])!=len(vrs[i][2]):
                break
            m=' '
            for j in range(len(vrs[i][2])):
                if n[i+1][j]==vrs[i][2][j]:
                    m+='.'
                else:
                    m+=n[i+1][j]
            l+=m+' '*(b[i]-len(m)+1)
        else:
            f.write(l+'\n')
    f.close()
    print('  Selected sequence alignments were saved into file: '+fname+'\n')

def heatmap(fig,plots,a,title,score,xlabel,ylabel):
    plt.subplot(1,plots,a)
    plt.title(title,size=13,weight='roman')
    ax=plt.gca()
    plt.imshow(score,aspect='auto',cmap='RdBu')
    ax.set_xticks(range(len(xlabel)))
    ax.set_xticklabels(xlabel,size=8,rotation=90)
    ax.set_yticks(range(len(ylabel)))
    ysize=8
    if len(ylabel)>70:
        ysize=5
    elif 50<len(ylabel)<=70:
        ysize=6
    elif 30<len(ylabel)<=50:
        ysize=7
    ax.set_yticklabels(ylabel,size=ysize)
    lim=(max([n for m in score for n in m])-min([n for m in score for n in m]))/2
    plt.clim(-lim, lim)
    if a!=1 or len(ylabel)>99:
        ax.axes.get_yaxis().set_visible(False)

def f2dl(fname,x,y):
    dbl.check_file(fname,True)
    f=open(fname,'r')
    temp=f.readlines()
    f.close()
    total=int(temp[0])
    temp=temp[1:]
    if not x:
        dic={}
        for n in temp:
            q=n.split()[:2]
            dic[q[0]]=int(q[1])
        return dic,total
    I=[x.index(m) for m in y]
    dic=defaultdict(int)
    for j in range(len(temp)):
        q=temp[j].split()[:2]
        z=tuple(q[0].split(',')[i] for i in I)
        dic[z]+=int(q[1])
    return dic,total

def cmap(n,map):
    mx=map[-1]
    map=map[:-1]
    for a,b in map:
        if n<a:
            return b
    else:
        return mx

def readmix(path):
    f=open(path+'caplib3_mix.txt','r')
    read=''
    input=[]
    ratio=[]
    output=''
    for line in f:
        line=line.strip()
        if line[:7]=='# INPUT':
            read='input'
        if line[:7]=='# RATIO':
            read='ratio'
        if line[:8]=='# OUTPUT':
            read='output'
        if line[:2]=='# ' or line[:13]=='Instructions:' or not line:
            continue
        if read=='input':
            input.append(line.split())
        elif read=='ratio':
            if not line.replace('.','').isdigit():
                print('  Only numbers should be entered in the RATIO section, 1 per line!\n')
                sys.exit()
            ratio.append(float(line))
        elif read=='output':
            if output:
                print('  A single file prefix should be entered in the output section!\n')
                sys.exit()
            output=line
    if len(input)!=len(ratio):
        print('  INPUT and RATIO must have the same number of lines!\n')
        sys.exit()
    x=sum(ratio)
    ratio=[n/x for n in ratio]
    return input,ratio,output

if __name__ == '__main__':
    main()
