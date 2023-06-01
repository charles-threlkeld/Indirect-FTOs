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
