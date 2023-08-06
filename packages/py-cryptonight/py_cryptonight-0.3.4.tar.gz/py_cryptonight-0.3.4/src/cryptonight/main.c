#include "hash-ops.h"

int main(int argc, char* argv[]){
  char hash[64];
  char * input = {"test"};
  cn_slow_hash(input, 4, hash, 4, 0, 0);
  cn_slow_hash(input, 4, hash, 4, 0, 0);
  return 0;
}