import re, os

def make_header():
    '''
    Create header including logo
    '''

    ascii_art = '''
               (((((((((((((((((((          
           (((((((((((((((((((((((((((      
         ((((((((((((((((                   
       (((((((((((((((((( ,,,,  ,,,,,,,,,,  
      ((((((((((((((((((  ,,,,, ,,,,,   ,,, 
     (((((((((((((((((((  ,,,,,,,,,,,,,,,,,,
     ((((((((((((((((((  ,,,,,,,,,,,,,,,,,,,
     ((((((((((((((((((  ,,,,,,,,,,,,,,,,,,,
     (((  ((((((  ((((( ,,,,,,,,,,,,,,,,,,,,
     ((((((   ,,,  (((  ,,,,,,,,,,,,,,,,,,,,
      (  ,,,,,,,,,  ((  ,,,,,,,,,,,,,,,,,,, 
       ,,,,,,,,,,,,    ,,,,,,,,,,,,,,,,,,,  
         ,,,,,,,,,,,   ,,,,,,,,,,,,,,,,,,   
           ,,,,,,,,,,,,,,,,,,,,,,,,,,,      
              ,,,,,,,,,,,,,,,,,,,,,         
    '''

    ansi_art = '''
    {e}{e}{e}{e}{e}{e}{e}{e}{e}{e}{e}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{e}{e}{e}{e}{e}{e}{e}{e}{e}{e}
    {e}{e}{e}{e}{e}{e}{e}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{e}{e}{e}{e}{e}{e}
    {e}{e}{e}{e}{e}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{r}{r}{r}{r}{r}{r}{r}{r}{r}{r}{r}{r}{r}{r}{r}{r}{e}{e}{e}
    {e}{e}{e}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{r}{b}{b}{b}{b}{e}{e}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{e}{e}
    {e}{e}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{r}{r}{b}{b}{b}{b}{b}{e}{b}{b}{b}{b}{b}{t}{t}{t}{b}{b}{b}{e}
    {e}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{r}{r}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}
    {e}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{r}{r}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}
    {e}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{t}{r}{r}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}
    {e}{t}{t}{t}{b}{b}{t}{t}{t}{t}{t}{t}{r}{r}{t}{t}{t}{t}{t}{r}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}
    {e}{t}{t}{t}{t}{t}{t}{r}{r}{r}{b}{b}{b}{r}{r}{t}{t}{t}{r}{r}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}
    {e}{e}{t}{r}{r}{b}{b}{b}{b}{b}{b}{b}{b}{b}{r}{r}{t}{t}{r}{r}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{e}
    {e}{e}{e}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{r}{r}{r}{r}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{e}{e}
    {e}{e}{e}{e}{e}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{r}{r}{r}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{e}{e}{e}
    {e}{e}{e}{e}{e}{e}{e}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{e}{e}{e}{e}{e}{e}
    {e}{e}{e}{e}{e}{e}{e}{e}{e}{e}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{b}{e}{e}{e}{e}{e}{e}{e}{e}{e}
    '''

    text_title='''
    ===========================================
        ____        __  __    _               
       / __ \__  __/ /_/ /_  (_)_  ______ ___ 
      / /_/ / / / / __/ __ \/ / / / / __ `__ \\
     / ____/ /_/ / /_/ / / / / /_/ / / / / / /
    /_/    \__, /\__/_/ /_/_/\__,_/_/ /_/ /_/ 
          /____/
    ===========================================
    '''
    e = '''[38;5;m '''
    r = '''\033[5m[38;5;087m*\033[0m'''
    b = '''[38;5;061m%'''
    t = '''[38;5;221m%'''
    RESET_SEQ = "\033[0m"
    print(text_title)
    if os.getenv('ANSI_COLORS_DISABLED') is None:
        ansi_art = re.sub('{e}',e, ansi_art)
        ansi_art = re.sub('{r}',r, ansi_art)
        ansi_art = re.sub('{t}',t, ansi_art)
        ansi_art = re.sub('{b}',b, ansi_art)
        print(ansi_art+RESET_SEQ)
    else:
        print(ascii_art)

if __name__ == '__main__':
    make_header()
