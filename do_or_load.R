# do_or_load.R
# (C) 2021 J.P. de Ruiter
# Tufts University
#
# DESCRIPTION
# Function to load a variable if it is stored as the file <variable.rdata> in 
# the same folder, or otherwise compute it and save it in that file for next time. 
#
# usage: do_or_load(variable_name, command, verbose = False)
# 
# Arguments:
# variable_name: a string representing the name of the variable the result is stored in
# command: an R function with a return value
# verbose: whether it informs us about the loading / computing

do_or_load <- function(variable_name, command, verbose = FALSE) {
  filename <- paste("tmp/",variable_name,".rdata",sep="")
  if(file.exists(filename)) {
    if(verbose) {
      message("Loading ",variable_name," from file '",filename,"'")
    }
    load(filename,envir=.GlobalEnv)
  } else {
    if(verbose) {
      message("computing and saving ",variable_name)
    }
    do.call("<<-", list(variable_name, command))
    do.call("save",list(variable_name, file=filename))
  }
}

# example (execute twice to test)
# dep <- rnorm(100,1,1)
# indep <- rnorm(100,1,1)
# do_or_load("mymodel",lm(dep ~ indep),verbose=TRUE)
# creates variable mymodel, and either retrieves it from the file 'mymodel.rdata' or computes and stores it there.


