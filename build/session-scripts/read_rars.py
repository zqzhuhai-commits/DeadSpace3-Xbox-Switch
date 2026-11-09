import ctypes as C,pathlib
l=C.CDLL('libarchive.so.13')
def setup(n,rest,args):
 f=getattr(l,n);f.restype=rest;f.argtypes=args;return f
a_new=setup('archive_read_new',C.c_void_p,[])
for n in ['archive_read_support_filter_all','archive_read_support_format_all','archive_read_free']:setup(n,C.c_int,[C.c_void_p])
setup('archive_read_open_filename',C.c_int,[C.c_void_p,C.c_char_p,C.c_size_t]);setup('archive_read_next_header',C.c_int,[C.c_void_p,C.POINTER(C.c_void_p)])
setup('archive_entry_pathname',C.c_char_p,[C.c_void_p]);setup('archive_entry_size',C.c_int64,[C.c_void_p]);setup('archive_read_data',C.c_ssize_t,[C.c_void_p,C.c_void_p,C.c_size_t]);setup('archive_error_string',C.c_char_p,[C.c_void_p])
for name in ['dlc','tu']:
 p=next(pathlib.Path('/workspace/attachments').rglob(name+'.rar'));out=pathlib.Path('/workspace/ds3-analysis/inputs')/name;out.mkdir(parents=True,exist_ok=True)
 a=a_new();l.archive_read_support_filter_all(a);l.archive_read_support_format_all(a)
 assert l.archive_read_open_filename(a,str(p).encode(),10240)==0
 e=C.c_void_p();idx=0
 while True:
  rc=l.archive_read_next_header(a,C.byref(e))
  if rc==1:break
  if rc<0:raise RuntimeError(l.archive_error_string(a))
  path=l.archive_entry_pathname(e).decode(errors='replace');size=l.archive_entry_size(e);print(name,path,size)
  if size:
   dest=out/(str(idx)+'-'+pathlib.PurePosixPath(path.replace('\\','/')).name);idx+=1
   with dest.open('wb') as f:
    buf=C.create_string_buffer(1048576)
    while True:
     n=l.archive_read_data(a,buf,len(buf))
     if n<0:raise RuntimeError(l.archive_error_string(a))
     if not n:break
     f.write(buf.raw[:n])
   assert dest.stat().st_size==size
 l.archive_read_free(a)
