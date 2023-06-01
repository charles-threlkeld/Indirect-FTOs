library(rstanarm)
library(bayestestR)

setwd("/home/chas/Projects/Indirect-FTOs/")
source("do_or_load.R")
ftodata <- read.csv("sentence_ftos.csv",
                    header=TRUE,
                    na.strings = c("NaN"))
ftodata$convo_num <- as.factor(ftodata$convo_num)

SAMPLES <- 50000 #change back to 50000 at some point
options(mc.cores = parallel::detectCores())

summary_stan_model<-function(mod,nfixefs=3){ #number of fixed effects
  samples_m1 <- as.data.frame(mod)
  nfixefs<-nfixefs + 1 ## to including intercept
  mns<-rep(NA,nfixefs)
  ci95<-matrix(rep(NA,nfixefs*2),ncol=2)
  for(i in 1:nfixefs){
    condnames<-colnames(samples_m1)[1:nfixefs]
    condnames[1]<-"Intercept"
    mns[i]<-round(mean(samples_m1[,i]),digits=4) 
    ci95[i,]<-round(quantile(probs=c(0.025,0.975),samples_m1[,i]),digits=4)
  }
  ## prob less than 0
  prob_less<-rep(NA,nfixefs)
  prob_more <-rep(NA,nfixefs)
  for(i in 1:nfixefs){
    prob_more[i]<-round(mean(samples_m1[,i]>0),digits=2)
    prob_less[i]<-round(mean(samples_m1[,i]<0),digits=2)
  }
  res<-as.data.frame(cbind(condnames,mns,ci95,prob_more, prob_less))
#  colnames(res)<-c("comparison","mean","lower","upper","P(b>0)", "P(b<0)")
  colnames(res)<-c(mod$formula,"mean","lower","upper","P(b>0)", "P(b<0)")
  return(res)
}

#####################################
## Models correcting for convo_num ##
#####################################

do_or_load("null_model",
           stan_lmer(fto ~ (1|convo_num),
                     data = ftodata,
                     chains = 4,
                     iter = SAMPLES,
                     diagnostic_file = "null_model.csv", 
                     refresh = 0))

do_or_load("speech_act",
           stan_lmer(fto ~ speech_act + (1|convo_num), 
                     data = ftodata,
                     chains = 4,
                     iter = SAMPLES,
                     diagnostic_file = "speech_act.csv", 
                     refresh = 0))

do_or_load("bf_speech_act",
           bayesfactor_models(null_model,
                              speech_act,
                              denominator = null_model))

do_or_load("sentence_type",
           stan_lmer(fto ~ sentence_type + (1|convo_num), 
                     data = ftodata,
                     chains = 4,
                     iter = SAMPLES,
                     diagnostic_file = "sentence_type.csv", 
                     refresh = 0))

do_or_load("bf_sentence_type",
           bayesfactor_models(null_model,
                              sentence_type,
                              denominator = null_model))


do_or_load("speech_act_interaction",
           stan_lmer(fto ~ speech_act + speech_act*sentence_type + (1|convo_num), 
                     data = ftodata,
                     chains = 4,
                     iter = SAMPLES,
                     diagnostic_file = "speech_act_sentence_type.csv", 
                     refresh = 0))

  
do_or_load("bf_speech_act_interaction",
           bayesfactor_models(speech_act,
                              speech_act_interaction,
                              denominator = speech_act))


do_or_load("addition_model",
           stan_lmer(fto ~ sentence_type + speech_act + (1|convo_num), 
                     data = ftodata,
                     chains = 4,
                     iter = SAMPLES,
                     diagnostic_file = "addition_model.csv", 
                     refresh = 0))

do_or_load("bf_addition",
           bayesfactor_models(null_model,
                              addition_model,
                              denominator = null_model))

do_or_load("interaction_model",
           stan_lmer(fto ~ sentence_type * speech_act + (1|convo_num), 
                     data = ftodata,
                     chains = 4,
                     iter = SAMPLES,
                     diagnostic_file = "interaction_model.csv", 
                     refresh = 0))

do_or_load("bf_interaction",
           bayesfactor_models(null_model,
                              interaction_model,
                              denominator = null_model))

do_or_load("bf_speech_act_addition",
           bayesfactor_models(speech_act,
                              addition_model,
                              denominator = speech_act))


summary_stan_model(null_model, 1)
summary_stan_model(sentence_type, 1)
summary_stan_model(speech_act, 1)
summary_stan_model(addition_model, 1)
summary_stan_model(interaction_model, 1)

message("Sentence Type / Null Bayes Factor:")
bf_sentence_type
message("Speech Act / Null Bayes Factor:")
bf_speech_act
message("Addition / Null Bayes Factor:")
bf_addition
message("Addition / Speech Act Bayes Factor:")
bf_speech_act_addition
message("Interaction / Null Bayes Factor:")
bf_interaction
message("Speech Act + Interaction / Speech Act Bayes Factor:")
bf_speech_act_interaction
