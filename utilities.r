
main<-function() {
    print(hypergeometric(61,6,3000,40))
    print(hypergeometric_ge(61,6,3000,40))
}

#Combintation n, k
comb<-function(n,k) {
    if(k == 0) return(1)
    p<-1
    for(i in 0:(k-1)) { p<-p*(n-i) }
    return(p/factorial(k))
}

# Hypergeometric pmf P(X = k)
hypergeometric<-function(n, k, N, m) {
    return(comb(m,k)*comb(N-m,n-k)/comb(N,n))
}

# Hypergeometric greater or equal: P(X >=k ) under hypergeometric distribution assumption
hypergeometric_ge<-function(n, k, N, m) {
    s<-0
    for(i in k:n) s<-s+hypergeometric(n, k, N, m)
    #for(i in 0:n) s<-s+hypergeometric(n, i, N, m)
    return(s)
}

# Correlation of two random variables
correlation<-function() {
    #df<-read.table("aneurysm_seed_scores.txt")
    d<-read.table("/home/emre/arastirma/data/aneurist/aneurist_Jul_05/aneursym_scores.txt")#, header=T)
    e<-read.table("/home/emre/arastirma/data/HEFalMp_predicted_gene_disease_associations/aneurysm_seed_pvalues.txt")
    df<-cbind(d,e)
    cor(df[,1], 1/df[,2])
    plot(df[,1], 1/df[,2], xlab="tm score", ylab="1 / p value")
}


# Behaviour of some polynomials
powers<-function() {
    x<-seq(1,10)
    xl<-seq(1,10) # seq(0,100,1)
    e<-exp(1)

    #postscript("den.ps", width = 5, height = 5, horizontal = FALSE, onefile = FALSE, paper = "special")

    plot(xl, x^-x, type="p", xlab="x", ylab="y", xlim=range(1,10))
    axis(1, at=seq(1,10,1))
    axis(2, at=seq(0,1,0.1))
    #lines(xl, e^-x, col=2, lty=3) 
    points(xl, x^-(x+1), col=2, pch="x") 
    #lines(xl, x^-e, col=3, lty=4) 
    lines(xl, x^-3, col=3, lty=3) 
    lines(xl, x^-2, col=4, lty=4) 
    lines(xl, x^-1, col=5, lty=1) 
    lines(xl, e^-(x-1), col=7, lty=2) 
    #par(lty=1)
    #lines(xl, x^-(0.5), col=7) 
    #lines(xl, x^-(2.5), col=8) 
    #lines(xl, x^-0, col=7) 
    #plot(xl, x^-2, type="p", col=7) 

    #legend("topright", c("x^-x", "e^-x", "x^-e", "x^-3", "x^-2", "x^-1", "x^-0"), col=c(1,2,3,4,5,6,7), lty=c(1,1,1,1,1,1,1))
    legend("topright", c("x^-1", "x^-2", "x^-3", "x^-x", "x^-(x+1)", "10^-x"), col=c(5,4,3,1,2,7), lty=c(1,4,3,0,0,2), pch=c("","","","o","x",""))

    #dev.off()
}

main()
