import subprocess as sp
import pandas as pd
import os
from termcolor import colored
class detail:
    def __init__(self):
        pass
    def array(self,resource):
        array=sp.getoutput(f'{resource}s --units g |grep -v swap')
        return [x.split() for x in array.split('\n')]
    def HD(self):
        array=sp.getoutput('ls /dev/sd* | grep -v /dev/sda').split('\n')
        for i in array:
            if(len(i)==9):
                array.remove(i[:-1])
        arr=[]
        for i in array:
            size=sp.getoutput(f'lsblk | grep {i[i.rindex("/")+1:]}').split()[3]
            arr.append([i,size])
        return pd.DataFrame(arr,columns=['HD','Size'])
    def PV(self):
        array=self.array('pv')
        for i in array:
            if(len(i)==5):
                i[1]=""
        return pd.DataFrame([i[0:2] for i in array][1:],columns=['PV','VG'])
    def VG(self):
        array=[i for i in self.array('vg')]
        return pd.DataFrame(array[1:],columns=array[0])
    def LV(self):
        array=[i for i in self.array('lv')]
        return pd.DataFrame(array[1:],columns=array[0][:4])
resource=[['Physical Volume','PV'],['Volume Group','VG'],['Logical Volume','LV'],['Secondary HardDisk','HD']]
wtd=['list','create','remove','extend','reduce']
r_size = int(os.get_terminal_size().columns/2)-10
c_size = os.get_terminal_size().columns
while True:
    print('\033c')
    ################ resource ################
    print("welcome to lvm world".center(c_size))
    print('________________________________________'.center(c_size))
    for i in range(len(resource)):
        print(''.rjust(r_size)+ f'"{i}"  :  {resource[i][0]}')
    print(''.rjust(r_size)+ '"q"  :  To exit')
    resource_no = input("Enter your choice: ")
    if(resource_no=="q"):
        break
    #os.system(' tput cup 3 0 && tput ed')
    print('\033c')
    ############ action ############
    if('0'<=resource_no<='3' and '.' not in resource_no):
        print(f'{resource[int(resource_no)][0]}'.center(c_size))
        print('________________________________________'.center(c_size))
    else:
        continue    
    if(resource_no=="1" or resource_no=="2"):
        for y in range(5):
            print(''.rjust(r_size+4)+ f'"{y}"  :  {wtd[y]}')
    elif(resource_no=="0"):
        for y in range(3):
            print(''.rjust(r_size+4)+ f'"{y}"  :  {wtd[y]}')
    else:
        for y in range(1):
            print(''.rjust(r_size+4)+ f'"{y}"  :  list')  
    print('' .rjust(r_size+4)+ '"q"  :  To back/cancel')
    while True:
        wtd_no=input("Enter your choice: ")
        os.system(' tput cup 9 0 && tput ed')
        if(wtd_no=="q"):
            break
        elif not ('0'<=wtd_no<=str(y) and '.' not in wtd_no):
             print(colored('Invalid Choice!!','red'))
             continue
        elif(wtd_no=="1"):
            data=getattr(detail(),resource[int(resource_no)-1][1])()
            if(resource_no=='0'):
                data1=getattr(detail(),'PV')()
                for i in data1.index:
                    data=data[data.iloc[:,0]!=data1.iloc[i,0]]
            elif(resource_no=='1'):
                data=data[data.iloc[:,1]=='']
            else:
                data.drop(data[data['VFree']=='0.00g'].index,inplace=True)
                data.drop(data[data['VFree']=='0g'].index,inplace=True)
            data.reset_index(drop=True,inplace=True)
        else:
            data=getattr(detail(),resource[int(resource_no)][1])()
        if(wtd_no=='4' or wtd_no=='2'):
            data.drop(data[data['VG']=='rhel'].index,inplace=True)
            data.reset_index(drop=True,inplace=True)
        if(len(data)!=0):
            print(colored(data,'cyan'))
            if(wtd_no!="0" ):
                hrdsc_no=input(colored(f'select a number to {wtd[int(wtd_no)]} {resource[int(resource_no)][0]}: ','green'))
                if("0"<=hrdsc_no<str(len(data)) and '.' not in hrdsc_no):
                    pass
                else:
                    os.system(' tput cup 9 0 && tput ed')
                    if(hrdsc_no=='q'):
                        print(colored('Operation cancelled!!','magenta'))
                    else:
                        print(colored('Invalid Choice!!','red'))
                    continue
                ######## pv ########
                if(resource_no=="0"):
                    if(wtd_no=="2" and data.iloc[int(hrdsc_no),1]!=''):
                        os.system(' tput cup 9 0 && tput ed')
                        print(colored(f"target '{data.iloc[int(hrdsc_no),0]}' is busy",'red'))
                        continue
                    print(sp.getoutput(f'pv{wtd[int(wtd_no)]} {data.iloc[int(hrdsc_no),0]}'))
                ######## vg ########
                elif(resource_no=="1"):
                    const=1
                    ### create ###
                    if(wtd_no=="1"):
                        hdd=[int(hrdsc_no)]
                    ### remove ###
                    elif(wtd_no=="2"):
                        if(data.iloc[int(hrdsc_no),2]!='0'):
                            os.system(' tput cup 9 0 && tput ed')
                            print(colored(f"target '{data.iloc[int(hrdsc_no),0]}' is busy",'red'))
                            continue
                        hdd=[int(hrdsc_no)]
                    else:
                        vgchoose=data.iloc[int(hrdsc_no),0]
                        ### extend ###
                        if(wtd_no=="3"):
                            data1=getattr(detail(),'PV')()
                            data=data1[data1.iloc[:,1]=='']
                        else:### reduce ###
                            data1=getattr(detail(),'PV')()
                            data=data1[data1.iloc[:,1]==vgchoose]
                            const=2
                        data=data.reset_index(drop=True)
                        if(len(data)>0):
                            print(data)
                            no=input(colored(f'select pv to extend Volume group: ','green'))
                            if('0'<=no<str(len(data))):
                                hdd=[int(no)]
                            else:
                                os.system(' tput cup 9 0 && tput ed')
                                if(no=='q'):
                                    print(colored('Operation cancelled!!','magenta'))
                                else:
                                    print(colored('Invalid Choice!!','red'))
                                continue
                        else:
                            print(f'you do not have any physical volume to {wtd[int(wtd_no)]}')
                            continue
                    for i in range(len(data)-const):
                        print(colored(data.drop(hdd),'cyan'))
                        x=input(colored('select more if you want or','green')+' "n" '+colored('to go for next: ','green'))
                        if(x=="n"):
                            pass
                        elif(int(x) not in hdd and '.' not in x and "0"<=x<str(len(data))):
                            hdd.append(int(x))
                        else:
                            os.system(' tput cup 9 0 && tput ed')
                            if(x=='q'):
                                print(colored('Operation cancelled!!','magenta'))
                            else:
                                print(colored('Invalid Choice!!','red'))
                            continue
                    hd=''
                    for i in hdd:
                        hd=hd+' '+data.iloc[i,0]
                    if(wtd_no=="1"):
                        name=input('Give a name: ')
                        if(name=='q'):
                            os.system(' tput cup 9 0 && tput ed')
                            print(colored('operation cancelled','magenta'))
                            continue
                        hd=f'{name} {hd}'
                    elif(wtd_no!='2'):
                        hd=f'{vgchoose} {hd}'
                    print(sp.getoutput(f'vg{wtd[int(wtd_no)]} {hd}'))
                else:######## lv ########
                    lv_name=data.iloc[int(hrdsc_no),0]
                    vg_name=data.iloc[int(hrdsc_no),1]
                    lv_path=f'/dev/mapper/{vg_name}-{lv_name}'
                    mountdetail=sp.getoutput(f'df -BG |grep {vg_name}-{lv_name}').split()
                    ### remove ###
                    if(wtd_no=='2'):
                        if(len(mountdetail)!=0):
                            ans=input(colored(f'Logical volume "{lv_name}" is mounted on {mountdetail[-1]}\nDo you want to unmount it(y/n): ','red'))
                            if(ans=='y'):
                                print(sp.getoutput(f'umount {mountdetail[-1]}'))
                            else:
                                os.system(' tput cup 9 0 && tput ed')
                                print(colored('Operation Cancelled !!','magenta'))
                                continue
                        print(sp.getoutput(f'lvremove {lv_path} -y'))
                    else:
                        size=input(colored('Enter the final Size(GB) of Logical Volume: ','green'))
                    ### create ###
                    if(wtd_no=='1'):
                        try:
                            compsize=data.iloc[int(hrdsc_no),6].replace('<','')
                            if(float(size)>float(compsize[:-1])):
                                print(colored('Insufficient size !!','red'))
                                continue
                        except:
                            os.system(' tput cup 9 0 && tput ed')
                            if(size=='q'):
                                print(colored('Operation cancelled!!','magenta'))
                            else:
                                print(colored('Invalid Input!!','red'))
                            continue
                        name=input('Give a name: ')
                        if(name=='q'):
                            os.system(' tput cup 9 0 && tput ed')
                            print(colored('operation cancelled','magenta'))
                            continue
                        com=sp.getstatusoutput(f'lvcreate --size {size}g --name {name} {lv_name} -y')
                        print(com[1])
                        if(com[0]==0):
                            sp.getoutput(f'mkfs.ext4 /dev/mapper/{lv_name}-{name}')
                            ans=input(f'Do you want to mount it(y/n): ')
                            if(ans=='y'):
                                while True:
                                    directory=input('mount to : ')
                                    if(directory=='q'):
                                        os.system(' tput cup 9 0 && tput ed')
                                        print(colored('operation cancelled','magenta'))
                                        break
                                    if not os.path.isdir(directory):
                                        ans=input(f'{directory} does not exist\nDo you want to create it (y/n): ')
                                        if(ans=='y'):
                                            sp.getoutput(f'mkdir {directory}')
                                        else:
                                            os.system(' tput cup 9 0 && tput ed')
                                            print(colored('Mount Operation Cancelled !!','magenta'))
                                            break
                                    else:
                                        if(sp.getoutput(f'du -sh {directory}').split()[0]!='0'):
                                            print(colored(f'{directory} has some data already','red'))
                                            continue
                                    mt=sp.getstatusoutput(f'mount /dev/mapper/{lv_name}-{name} {directory}')[0]
                                    if(mt==0):
                                        print(colored('Mounted successfully','green'))
                                    else:
                                        print(colored(f'New directory {directory} created but mount operation failed due to some reason','magenta'))
                                    break
                                continue
                            else:
                                os.system(' tput cup 9 0 && tput ed')
                                continue
                    ### extend ###
                    elif(wtd_no=='3'):    
                        print(sp.getoutput(f'lvextend --size {size}g {lv_path} -y'))
                    ### reduce ###
                    elif(wtd_no=='4'):
                        if(len(mountdetail)!=0):
                           if(mountdetail[2][:-1]<size): 
                               sp.getoutput(f'umount {mountdetail[-1]}')
                           else:
                               os.system(' tput cup 9 0 && tput ed')
                               print(colored('Resource is occupied','red'))
                               continue
                        else:
                            sp.getoutput(f'mkdir /mszff_te2df')
                            um=sp.getstatusoutput(f'mount {lv_path} /mszff_te2df')[0]
                            if(um==0):
                                os.system(' tput cup 9 0 && tput ed')
                                print(colored(f"target '{lv_name}' is busy",'red'))
                                continue
                            temp_mount=sp.getoutput(f'df -BG |grep /mszff_te2df').split()
                            if(temp_mount[2]=='0'):
                                var='0'
                            #elif(temp_mount[2][-1]=='M'):
                             #   var=f'{int(temp_mount[2][:-1])/1000}'
                            else:
                                var=temp_mount[2][:-1]
                            sp.getoutput(f'umount /mszff_te2df')
                            if(float(var)<float(size)): 
                                sp.getoutput(f'rm -rf /mszff_te2df')
                            else:
                                os.system(' tput cup 9 0 && tput ed')
                                print(colored('Resource is occupied','red'))
                                continue
                        ask=input(colored(f'This may destroy your data!! okay (y/n): ','red'))
                        if(ask=='y'):
                            sp.getoutput(f'e2fsck -pf {lv_path}')
                            sp.getoutput(f'resize2fs {lv_path} {size}G')
                            print(sp.getoutput(f'lvreduce --size {size}g -f {lv_path}'))
                        else:
                            os.system(' tput cup 9 0 && tput ed')
                            print(colored('Operation Cancelled !!','magenta'))
                            continue
                        if(len(mountdetail)!=0):
                            sp.getoutput(f'mount {lv_path} {mountdetail[-1]}')
        else:
            if(wtd_no=='1' and resource_no!='3'):
                print(f'You do not have more {resource[int(resource_no)-1][0]} ')
            else:
                print(f'No {resource[int(resource_no)][0]} to {wtd[int(wtd_no)]}')
