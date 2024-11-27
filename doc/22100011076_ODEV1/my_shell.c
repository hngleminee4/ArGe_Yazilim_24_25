// Öğrenci No:22100011076
// Ad-Soyad:Emine Hangül
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <assert.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>

enum cmd_type {// bunlari tanimlamadan once hata veriyordu
    EXEC = 1,   // Basit komut
    REDIR,      // Girdi/Çıktı yönlendirme
    PIPE,       // Boru (pipe) komutu
    BACK        // Arka plan (background) komutu
};

// Simplifed xv6 shell.

#define MAXARGS 10

// All commands have at least a type. Have looked at the type, the code
// typically casts the *cmd to some specific cmd type.
struct cmd {
  int type;          //  ' ' (exec), | (pipe), '<' or '>' for redirection
};

struct backcmd {
    int type;          // '&'
    struct cmd *cmd;   // Arka planda çalıştırılacak komut
};

struct execcmd {
  int type;              // ' '
  char *argv[MAXARGS];   // arguments to the command to be exec-ed
};

struct redircmd {
  int type;          // < or >
  struct cmd *cmd;   // the command to be run (e.g., an execcmd)
  char *file;        // the input/output file
  int mode;          // the mode to open the file with
  int flags;        // Dosya açma bayrakları (O_RDONLY, O_WRONLY, vb.)
  int fd;            // the file descriptor number to use for the file
};

struct pipecmd {
  int type;          // |
  struct cmd *left;  // left side of pipe
  struct cmd *right; // right side of pipe
};

int fork1(void);  // Fork but exits on failure.
struct cmd *parsecmd(char*);

// Execute cmd.  Never returns.
void
runcmd(struct cmd *cmd)
{
  int p[2], r;
  struct execcmd *ecmd;
  struct pipecmd *pcmd;
  struct redircmd *rcmd;

  if(cmd == 0)
    exit(0);

  switch(cmd->type){
  default:
    fprintf(stderr, "unknown runcmd\n");
    exit(-1);

  case ' ':
    ecmd = (struct execcmd*)cmd;
    if(ecmd->argv[0] == 0)
      exit(0);
    fprintf(stderr, "exec not implemented\n");
    // -------------------------------------------------------
    // SORU 1: Basit komutlar için yazılacak kodlar buraya ...
    if (cmd->type == EXEC) {
    //komut tipi EXEC ise, execcmd yapısını alıyoruz
    struct execcmd *ecmd = (struct execcmd *)cmd;

    //eğer argv boşsa, bir komut verilmemiş demektir; geri dönüyoruz
    if (ecmd->argv[0] == 0) {
        fprintf(stderr, "No command found to execute.\n");
        return;
    }

    //yeni bir süreç oluşturuluyor
    pid_t pid = fork();
    if (pid < 0) {
        // Eğer fork başarısız olursa hata basılır
        perror("fork failed");
        return;
    }

    if (pid == 0) {
        //çocuk süreçteyiz; execvp ile komut çalıştırılır
        if (execvp(ecmd->argv[0], ecmd->argv) < 0) {
            fprintf(stderr, "Command execution failed: %s\n", ecmd->argv[0]);
            exit(EXIT_FAILURE);
        }
    } else {
        //ebeveyn süreç çocuğun bitmesini bekler
        int status;
        waitpid(pid, &status, 0);
    }
    return;
}

    // -------------------------------------------------------
    break;

  case '>':
  case '<':
    rcmd = (struct redircmd*)cmd;
    fprintf(stderr, "redir not implemented\n");
    // -------------------------------------------------------
    // SORU 2: I/O komutlar için yazılacak kodlar buraya ...
    if (cmd->type == REDIR) {
    struct redircmd *rcmd = (struct redircmd *)cmd;

    //yeni bir süreç oluşturuyoruz
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed for REDIR");
        return;
    }

    if (pid == 0) {
        //çocuk süreçte dosyayı açıyoruz
        int fd = open(rcmd->file, rcmd->flags, 0644);
        if (fd < 0) {
            fprintf(stderr, "Error opening file: %s\n", rcmd->file);
            exit(EXIT_FAILURE);
        }

        //dosya tanıtıcısını uygun standard input/output ile değiştiriyoruz
        if (dup2(fd, rcmd->fd) < 0) {
            perror("dup2 failed");
            close(fd);
            exit(EXIT_FAILURE);
        }
        close(fd);

        //asıl komutu çalıştırıyoruz
        runcmd(rcmd->cmd);
        exit(0);
    } else {
        //ebeveyn sürecin çocuğu beklemesi
        int status;
        waitpid(pid, &status, 0);
    }
    return;
}
    // -------------------------------------------------------
    runcmd(rcmd->cmd);
    break;

  case '|':
    pcmd = (struct pipecmd*)cmd;
    fprintf(stderr, "pipe not implemented\n");
    // -------------------------------------------------------
    // SORU 3: Sıralı komutlar için yazılacak kodlar buraya ...
    if (cmd->type == PIPE) {
    struct pipecmd *pcmd = (struct pipecmd *)cmd;

    //pipe için iki dosya tanıtıcısı
    int pipefd[2];
    if (pipe(pipefd) < 0) {
        perror("pipe failed");
        return;
    }

    //ilk çocuk süreç: Sol komut
    pid_t left_pid = fork();
    if (left_pid < 0) {
        perror("fork failed for left command");
        return;
    }

    if (left_pid == 0) {
        //sol komut için pipe'ın yazma ucunu standard output olarak ayarla
        close(pipefd[0]);
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[1]);

        runcmd(pcmd->left);
        exit(0);
    }

    //ikinci çocuk süreç: Sağ komut
    pid_t right_pid = fork();
    if (right_pid < 0) {
        perror("fork failed for right command");
        return;
    }

    if (right_pid == 0) {
        //sağ komut için pipe'ın okuma ucunu standard input olarak ayarla
        close(pipefd[1]);
        dup2(pipefd[0], STDIN_FILENO);
        close(pipefd[0]);

        runcmd(pcmd->right);
        exit(0);
    }

    //ebeveyn süreç: Pipe'ı kapat
    close(pipefd[0]);
    close(pipefd[1]);

    //çocukların bitmesini bekle
    waitpid(left_pid, NULL, 0);
    waitpid(right_pid, NULL, 0);
    return;
}
    // -------------------------------------------------------
    break;
  case '&':
    // -------------------------------------------------------
    // SORU 4: Paralel komutlar için yazılacak kodlar buraya ...
    if (cmd->type == BACK) {
    struct backcmd *bcmd = (struct backcmd *)cmd;

    // Yeni bir süreç oluşturuluyor
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed for BACK");
        return;
    }

    if (pid == 0) {
        // Çocuk süreçte komut çalıştırılır
        printf("Background process started with PID: %d\n", getpid());
        runcmd(bcmd->cmd);
        exit(0);
    } else {
        // Ebeveyn süreç çocuğu beklemez, kontrolü geri döner
        printf("Command running in background with PID: %d\n", pid);
    }
    return;
}
    // -------------------------------------------------------
    break;
  }
  exit(0);
}

int
getcmd(char *buf, int nbuf)
{

  if (isatty(fileno(stdin)))
    fprintf(stdout, "$ ");
  memset(buf, 0, nbuf);
  fgets(buf, nbuf, stdin);
  if(buf[0] == 0) // EOF
    return -1;
  return 0;
}

int
main(void)
{
  static char buf[100];
  int fd, r;

  // Read and run input commands.
  while(getcmd(buf, sizeof(buf)) >= 0){
    if(buf[0] == 'c' && buf[1] == 'd' && buf[2] == ' '){
      // Clumsy but will have to do for now.
      // Chdir has no effect on the parent if run in the child.
      buf[strlen(buf)-1] = 0;  // chop \n
      if(chdir(buf+3) < 0)
        fprintf(stderr, "cannot cd %s\n", buf+3);
      continue;
    }
    if(fork1() == 0)
      runcmd(parsecmd(buf));
    wait(&r);
  }
  exit(0);
}

int
fork1(void)
{
  int pid;

  pid = fork();
  if(pid == -1)
    perror("fork");
  return pid;
}

struct cmd*
execcmd(void)
{
  struct execcmd *cmd;

  cmd = malloc(sizeof(*cmd));
  memset(cmd, 0, sizeof(*cmd));
  cmd->type = ' ';
  return (struct cmd*)cmd;
}

struct cmd*
redircmd(struct cmd *subcmd, char *file, int type)
{
  struct redircmd *cmd;

  cmd = malloc(sizeof(*cmd));
  memset(cmd, 0, sizeof(*cmd));
  cmd->type = type;
  cmd->cmd = subcmd;
  cmd->file = file;
  cmd->mode = (type == '<') ?  O_RDONLY : O_WRONLY|O_CREAT|O_TRUNC;
  cmd->fd = (type == '<') ? 0 : 1;
  return (struct cmd*)cmd;
}

struct cmd*
pipecmd(struct cmd *left, struct cmd *right)
{
  struct pipecmd *cmd;

  cmd = malloc(sizeof(*cmd));
  memset(cmd, 0, sizeof(*cmd));
  cmd->type = '|';
  cmd->left = left;
  cmd->right = right;
  return (struct cmd*)cmd;
}

// Parsing

char whitespace[] = " \t\r\n\v";
char symbols[] = "<|>";

int
gettoken(char **ps, char *es, char **q, char **eq)
{
  char *s;
  int ret;

  s = *ps;
  while(s < es && strchr(whitespace, *s))
    s++;
  if(q)
    *q = s;
  ret = *s;
  switch(*s){
  case 0:
    break;
  case '|':
  case '<':
    s++;
    break;
  case '>':
    s++;
    break;
  default:
    ret = 'a';
    while(s < es && !strchr(whitespace, *s) && !strchr(symbols, *s))
      s++;
    break;
  }
  if(eq)
    *eq = s;

  while(s < es && strchr(whitespace, *s))
    s++;
  *ps = s;
  return ret;
}

int
peek(char **ps, char *es, char *toks)
{
  char *s;

  s = *ps;
  while(s < es && strchr(whitespace, *s))
    s++;
  *ps = s;
  return *s && strchr(toks, *s);
}

struct cmd *parseline(char**, char*);
struct cmd *parsepipe(char**, char*);
struct cmd *parseexec(char**, char*);

// make a copy of the characters in the input buffer, starting from s through es.
// null-terminate the copy to make it a string.
char
*mkcopy(char *s, char *es)
{
  int n = es - s;
  char *c = malloc(n+1);
  assert(c);
  strncpy(c, s, n);
  c[n] = 0;
  return c;
}

struct cmd*
parsecmd(char *s)
{
  char *es;
  struct cmd *cmd;

  es = s + strlen(s);
  cmd = parseline(&s, es);
  peek(&s, es, "");
  if(s != es){
    fprintf(stderr, "leftovers: %s\n", s);
    exit(-1);
  }
  return cmd;
}

struct cmd*
parseline(char **ps, char *es)
{
  struct cmd *cmd;
  cmd = parsepipe(ps, es);
  return cmd;
}

struct cmd*
parsepipe(char **ps, char *es)
{
  struct cmd *cmd;

  cmd = parseexec(ps, es);
  if(peek(ps, es, "|")){
    gettoken(ps, es, 0, 0);
    cmd = pipecmd(cmd, parsepipe(ps, es));
  }
  return cmd;
}

struct cmd*
parseredirs(struct cmd *cmd, char **ps, char *es)
{
  int tok;
  char *q, *eq;

  while(peek(ps, es, "<>")){
    tok = gettoken(ps, es, 0, 0);
    if(gettoken(ps, es, &q, &eq) != 'a') {
      fprintf(stderr, "missing file for redirection\n");
      exit(-1);
    }
    switch(tok){
    case '<':
      cmd = redircmd(cmd, mkcopy(q, eq), '<');
      break;
    case '>':
      cmd = redircmd(cmd, mkcopy(q, eq), '>');
      break;
    }
  }
  return cmd;
}

struct cmd*
parseexec(char **ps, char *es)
{
  char *q, *eq;
  int tok, argc;
  struct execcmd *cmd;
  struct cmd *ret;

  ret = execcmd();
  cmd = (struct execcmd*)ret;

  argc = 0;
  ret = parseredirs(ret, ps, es);
  while(!peek(ps, es, "|")){
    if((tok=gettoken(ps, es, &q, &eq)) == 0)
      break;
    if(tok != 'a') {
      fprintf(stderr, "syntax error\n");
      exit(-1);
    }
    cmd->argv[argc] = mkcopy(q, eq);
    argc++;
    if(argc >= MAXARGS) {
      fprintf(stderr, "too many args\n");
      exit(-1);
    }
    ret = parseredirs(ret, ps, es);
  }
  cmd->argv[argc] = 0;
  return ret;
}
