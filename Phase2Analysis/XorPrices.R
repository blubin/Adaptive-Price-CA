# Read in the XorPrices Data

source('common.R')
library(purrr)
library(tidyr)
library(reshape2)
library(gdata)
library(doBy)

options(dplyr.summarise.inform = FALSE)

#Specify the stepc we used:
stepc.arbitrary.adaptivecutting <- "0.02"
stepc.arbitrary.ibundle <- NA
stepc.arbitrary.linearclock <- "0.08"
stepc.arbitrary.linearexact <- "0.08"
stepc.arbitrary.linearpacking <- "0.08"

stepc.reg.adaptivecutting <- "0.02"
stepc.reg.ibundle <- NA
stepc.reg.linearclock <- "0.08"
stepc.reg.linearexact <- "0.02"
stepc.reg.linearpacking <- "0.04"

args = commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
  domain <- "arbitrary"
  #domain <- "reg"
  #domain <- "path"
} else if (length(args)==1) {
  domain = args[1]
}

# READING THE DATA
##################

# Read in instance files from a zip file 
read.prices.zip <- function(zipfile, subdir) {
  message('Reading ', zipfile, ' in ', subdir)
  
  #First look to see if we have a cache:
  data = get.cached(zipfile, subdir)
  if(!is.logical(data)) {
    print("Using Cached data")
    return(data)
  }
  
  # Get all files in the zip:
  ziplist <- unzip(zipfile, list=TRUE)$Name
  # Pull out only the price summary files:
  pricefiles <- grep(paste0(subdir,'/xorprices#.*csv'), ziplist, value=TRUE)
  # Get the data
  data <- do.call(bind_rows, lapply(pricefiles, 
                                    function(x){read.csv(unz(zipfile, x), stringsAsFactors=FALSE)}))

  data$epsilon <- as.factor(data$epsilon)
  data$epsilon <- reorder(data$epsilon)
  data$epoch <- as.factor(data$epoch)
  data$epoch <- reorder(data$epoch)
  data$stepc <- as.factor(data$stepc)
  data$stepc <- reorder(data$stepc)
  data$items <- as.factor(data$items)
  data$items <- reorder(data$items)
  data$generator_param_name <- as.factor(data$generator_param_name)
  data$generator_param_name <- reorder(data$generator_param_name)
  data$auction_class <- as.factor(data$auction_class)
  data$auction_class <- reorder(data$auction_class)
  set.cached(zipfile, subdir, data)
  return(data)
}

# Read in all the data:
# Note: Don't run AdaptiveHeuristicAuction. Should run AdptiveCuttingAuction
if(domain == "arbitrary") {
  print("Processing Arbitrary")
  adaptivecutting_prices   <- read.prices.zip(paste0('results/xorprices/xorprices#AdaptiveCuttingAuction#gen_cats_arbitrary_g30b150#stepc_',stepc.arbitrary.adaptivecutting,'_11_16_21.zip'),  'experiments/xorprices_cats_arbitrary_stepc')
}
if(domain == "reg") {
  print("Processing Regions")
  adaptivecutting_prices   <- read.prices.zip(paste0('results/xorprices/xorprices#AdaptiveCuttingAuction#gen_cats_reg_g30b150#stepc_',stepc.reg.adaptivecutting,'_11_16_21.zip'),  'experiments/xorprices_cats_reg_stepc')
}
if(domain == "path") {
  stop("Paths not processed for now, as it contains personalized prices")
}

###############################################################
## Start by taking 1-round differences in prices per bundle and 
## creating histograms of how many of these are positive to
## get a sense of monotonicity:

#[See: https://newbedev.com/use-dynamic-variable-names-in-dplyr]

# t <- adaptivecutting_prices %>% filter(idx==1)
# t <- t %>% select_if(~sum(!is.na(.)) >0)
# t <- t %>% select(X10.18) %>% mutate(bundle=X10.18) 
# t<-t %>% mutate(diff=bundle-lag(bundle,default=bundle[1]))
# t<-t %>% mutate(inc=diff>0)
# agg<-t %>% group_by(inc) %>% summarize(total_diff=sum(diff))
# plot(temp$round,temp$X0.17.27.25)

#lag_col <- function(x) {
#  #1-step lag, first element will be NA
#  lag(pull(x)) %>% as_tibble() %>% set_names(paste0(colnames(x),"")) 
#}

diff_col <- function(x) {
  #1-step lagged difference
  diff(pull(x)) %>% as_tibble() %>% set_names(paste0(colnames(x),"")) 
}

#num.idx = 1
num.idx = max(adaptivecutting_prices$idx)
posfracagg <- tibble(FracPos=numeric()) # Fraction of positive across all isntances
posfracweightedagg <- tibble(FracPosWeighted=numeric()) # Weighted fraction of positive across all isntances
numbundles <- tibble(NumBundles=numeric()) # Number of Bundles in each instance
for(i in 1:num.idx) {
  print(sprintf("Processing index %d...", i))
  # Restrict to one index
  idx_data <- adaptivecutting_prices %>% filter(idx==i)
  #drop NA columns:
  idx_data <- idx_data %>% select(where(~!any(is.na(.x))))
  #Get only the bundle columns
  bundle_data <- idx_data %>% select(starts_with("X"))
  #Get the diffs as a new dataframe:  
  diffs <- bind_cols(lapply(1:ncol(bundle_data), function(x){diff_col(bundle_data[x])}))
  #Set the zero level to be 1% of the median absolute value
  zerolevel = .01*diffs %>% mutate_all(abs) %>% summarize_all(median) %>% rowwise() %>% mutate(m=median(c_across(starts_with("X"))))%>% rowwise() %>% mutate(M=median(c_across(starts_with("X")))) %>% select(M) %>% as.numeric()
  #Set to NA all elements that are within +/- of zerolevel:
  nonzero <- diffs %>% mutate_all(function(c){case_when(abs(c)>zerolevel~c)})

  #Now get the fraction of positive values: 
  posfrac <- nonzero %>% summarize_all(function(c){sum(c>0, na.rm=TRUE)/length(c[!is.na(c)])})
  posfrac <- posfrac %>% mutate_all(replace_na, replace=0)
  #Now aggregate
  transposed<-posfrac %>% t
  colnames(transposed)[1] <- "FracPos"
  rownames(transposed) <- c()
  posfracagg<-rbind(posfracagg,transposed)
  
  #Now get a weighted fraction of positive values: 
  posfracweighted <- nonzero %>% summarize_all(function(c){sum(c[c>0], na.rm=TRUE)/sum(abs(c), na.rm=TRUE)})
  posfracweighted <- posfracweighted %>% mutate_all(replace_na, replace=0)
  #Now aggregate
  transposed<-posfracweighted %>% t
  colnames(transposed)[1] <- "FracPosWeighted"
  rownames(transposed) <- c()
  posfracweightedagg<-rbind(posfracweightedagg,transposed)
  
  numbundles<-rbind(numbundles, length(transposed))
}

capdomain <- tools::toTitleCase(domain)

# Unweighted

# Compute summary statistics:
f<-file(sprintf("tables/XorPrices/fracpos_%s.tex",domain))
writeLines(c(sprintf("\\newcommand{\\fracPosMean%s}{$%.2f$}", capdomain, mean(posfracagg$FracPos)),
             sprintf("\\newcommand{\\fracPosSD%s}{$%.2f$}", capdomain, sd(posfracagg$FracPos)),
             sprintf("\\newcommand{\\fracPosQZero%s}{$%.2f$}", capdomain, quantile(posfracagg$FracPos, names=FALSE)[1]),
             sprintf("\\newcommand{\\fracPosQTwentyFive%s}{$%.2f$}", capdomain, quantile(posfracagg$FracPos, names=FALSE)[2]),
             sprintf("\\newcommand{\\fracPosQFifty%s}{$%.2f$}", capdomain, quantile(posfracagg$FracPos, names=FALSE)[3]),
             sprintf("\\newcommand{\\fracPosQSeventyFive%s}{$%.2f$}", capdomain, quantile(posfracagg$FracPos, names=FALSE)[4]),
             sprintf("\\newcommand{\\fracPosQOneHundred%s}{$%.2f$}", capdomain, quantile(posfracagg$FracPos, names=FALSE)[5])), f)
close(f)

# Now plot a basic histogram:
ggplot(posfracagg, aes(x=FracPos)) + 
  theme_bw()+
  geom_histogram(bins=50) +
  geom_vline(aes(xintercept=median(FracPos)),
             color="palegreen", linetype="dashed", size=1)+
  annotate(geom="text",color="palegreen",
           label= paste0("Median=",format(round(median(posfracagg$FracPos),2),nsmall=2)),
           x=median(posfracagg$FracPos),
           y=max(hist(posfracagg$FracPos,breaks=50,plot=FALSE)$counts)/2,
           angle=90,vjust=1,hjust=1)+
  xlab("Fraction of Positive Price Increments") +
  ylab("Bundle Count")
ggsave(sprintf("plots/XorPrices/fracpos_%s.pdf",domain))

### # Weighting by the price change...  should look more monotone.

### # Compute summary statistics:
### f<-file(sprintf("tables/XorPrices/fracposweighted_%s.tex",domain))
### writeLines(c(sprintf("\\newcommand{\\fracPosWeightedMean%s}{$%.2f$}", capdomain, mean(posfracweightedagg$FracPosWeighted)),
###              sprintf("\\newcommand{\\fracPosWeightedSD%s}{$%.2f$}", capdomain, sd(posfracweightedagg$FracPosWeighted)),
###              sprintf("\\newcommand{\\fracPosWeightedQZero%s}{$%.2f$}", capdomain, quantile(posfracweightedagg$FracPosWeighted, names=FALSE)[1]),
###              sprintf("\\newcommand{\\fracPosWeightedQTwentyFive%s}{$%.2f$}", capdomain, quantile(posfracweightedagg$FracPosWeighted, names=FALSE)[2]),
###              sprintf("\\newcommand{\\fracPosWeightedQFifty%s}{$%.2f$}", capdomain, quantile(posfracweightedagg$FracPosWeighted, names=FALSE)[3]),
###              sprintf("\\newcommand{\\fracPosWeightedQSeventyFive%s}{$%.2f$}", capdomain, quantile(posfracweightedagg$FracPosWeighted, names=FALSE)[4]),
###              sprintf("\\newcommand{\\fracPosWeightedQOneHundred%s}{$%.2f$}", capdomain, quantile(posfracweightedagg$FracPosWeighted, names=FALSE)[5])), f)
### close(f)

### # Now plot a basic histogram:
### ggplot(posfracweightedagg, aes(x=FracPosWeighted)) + 
###   theme_bw()+
###   geom_histogram(bins=50) +
###   geom_vline(aes(xintercept=median(FracPosWeighted)),
###              color="palegreen", linetype="dashed", size=1)+
###   annotate(geom="text",color="palegreen",
###            label= paste0("Median=",format(round(median(posfracweightedagg$FracPosWeighted),2),nsmall=2)),
###            x=median(posfracweightedagg$FracPosWeighted),
###            y=max(hist(posfracweightedagg$FracPosWeighted,breaks=50,plot=FALSE)$counts)/2,
###            angle=90,vjust=1,hjust=1)+
###   xlab("Weighted Fraction of Positive Price Increments") +
###   ylab("Bundle Count")
### ggsave(sprintf("plots/XorPrices/fracposweighted_%s.pdf",domain))

################################################
## Now just plot some sample price trajectories:

num.idx = max(adaptivecutting_prices$idx)
largestbundle <- NULL
for(i in 1:num.idx) {
  print(sprintf("Processing index %d...", i))
  # Restrict to one index
  idx_data <- adaptivecutting_prices %>% filter(idx==i)
  #drop NA columns:
  idx_data <- idx_data %>% select(where(~!any(is.na(.x))))
  #Get only the bundle columns
  bundle_data <- idx_data %>% select(starts_with("X"))

  ### Code for putting all the plots of a single instance on one plot:
  #
  # # [ Handle the spaghetti, see: https://www.data-to-viz.com/caveat/spaghetti.html ]
  # # Plot all of the bundles on one plot:
  # # Add a round variable
  #   bundle_data <- bundle_data %>% mutate(round=1:length(bundle_data[[1]]))
  # # Melt the data for use in ggplot: (see: https://stackoverflow.com/questions/4877357/how-to-plot-all-the-columns-of-a-data-frame-in-r)
  #   meltedDF <- melt(bundle_data, id.vars='round', variable.name='bundle')
  # # Plot on single plot:
  #   ggplot(meltedDF, aes(round,value)) + 
  #     theme_bw()+
  #     theme(legend.position="none") +
  #     geom_line(aes(colour=bundle))
  
  ### Code for plotting a single plot per instance for the bundle with the largest initial price
  # 
  # # Find the bundle with the largest starting value (see https://stackoverflow.com/questions/17735859/for-each-row-return-the-column-name-of-the-largest-value):
  # biggest_bundle <- bundle_data %>% slice_head() %>% rowwise() %>% summarize(max = names(.)[which.max(c_across(everything()))])
  # # Extract that column:
  # df <- bundle_data[biggest_bundle[[1]]]
  # colnames(df)[1] <- "price"
  # #Add a round variable
  # df <- df %>% mutate(round=1:length(df[[1]]))
  # # Make a plot
  # ggplot(df, aes(round,price)) + 
  #   theme_bw()+
  #   geom_line()+
  #   geom_point()+
  #   xlab("Round") +
  #   ylab("Bundle Price")
  # ggsave(sprintf("plots/XorPrices/pricetrajectorylargest_%s_%d.pdf",domain,i))
  
  ### Code to accumulate the price trajectory for the bundle with the largest initial value across all instances
  # Find the bundle with the largest starting value (see https://stackoverflow.com/questions/17735859/for-each-row-return-the-column-name-of-the-largest-value):
  biggest_bundle <- bundle_data %>% slice_head() %>% rowwise() %>% summarize(max = names(.)[which.max(c_across(everything()))])
  # Extract that column:
  df <- bundle_data[biggest_bundle[[1]]]
  colnames(df)[1] <- i
  if(length(largestbundle)==0) {
    largestbundle<-df
  } else {
    largestbundle <- cbindX(largestbundle,df)
  }
}
largestbundle<- as_tibble(largestbundle)

### Plot many price trajectories on a single plot, highlight the trajectory which changes the most:
# Downselect to a smaller number of samples
cols <- 1:10
# # Downselect to a smaller number of samples, sorted by those with most NAs (shortest auctions)
# # (see: https://stackoverflow.com/questions/50496618/select-column-that-has-the-fewest-na-values)
#cols <- which.maxn(unlist(largestbundle %>% map(function(x) sum(is.na(x)))), 33)
selected <- largestbundle %>% select(all_of(cols))
selected <- selected %>% filter(!if_all(everything(), ~ is.na(.x)))
# Get a list of the spreads of each index 
spread <- selected %>% map(function(x){max(x, na.rm=TRUE)-min(x, na.rm=TRUE)})
biggest_spread <- names(spread)[which.max(spread)]
# Add a round variable
selected <- selected %>% mutate(round=1:length(selected[[1]]))
# Melt the data for use in ggplot: (see: https://stackoverflow.com/questions/4877357/how-to-plot-all-the-columns-of-a-data-frame-in-r)
meltedDF <- melt(selected, id.vars='round', variable.name='index')
meltedDF <- meltedDF %>% filter(!if_any(everything(), ~ is.na(.x)))
# Handle the spaghetti, see: https://www.data-to-viz.com/caveat/spaghetti.html 
meltedDF <- meltedDF %>% mutate( highlight = index==biggest_spread)
# Plot on single plot:
ggplot(meltedDF, aes(round,value, group=index, color=highlight, size=highlight)) + 
  theme_bw()+
  scale_color_manual(values = c("lightgrey", "royalblue")) +
  scale_size_manual(values=c(.5,1)) +
  theme(legend.position="none") +
  geom_line() +
  xlab("Round") +
  ylab("Bundle Price")
ggsave(sprintf("plots/XorPrices/pricetrajectorylargestVisA_%s.pdf",domain))

### selected <- largestbundle %>% mutate(round=1:length(largestbundle[[1]]))
### spread <- selected %>% map(function(x){max(x, na.rm=TRUE)-min(x, na.rm=TRUE)})
### biggest_spread <- names(spread)[which.max(spread)]
### selected <- selected %>% mutate(round=1:length(selected[[1]]))
### # Melt the data for use in ggplot: (see: https://stackoverflow.com/questions/4877357/how-to-plot-all-the-columns-of-a-data-frame-in-r)
### meltedDF <- melt(selected, id.vars='round', variable.name='index')
### meltedDF <- meltedDF %>% filter(!if_any(everything(), ~ is.na(.x)))
### # Handle the spaghetti, see: https://www.data-to-viz.com/caveat/spaghetti.html 
### lineDF <- meltedDF %>% filter(index==biggest_spread)
### # Plot on single plot a hexplot:
### ggplot(meltedDF, aes(round,value)) +
###   theme_bw() +
###   #geom_hex(bins=100) +
###   stat_density_2d(aes(fill = ..density.., alpha=..density..), n=200, h=c(10,25), geom = "raster", contour = FALSE) +
###   scale_x_continuous(expand = c(0, 0), limits=c(0,300)) +
###   scale_y_continuous(expand = c(0, 0)) +
###   theme(legend.position='none') +
###   #scale_fill_continuous(type = "viridis") +
###   scale_alpha_continuous(range = c(0, 1), limits = c(0, 1e-6), guide = guide_none()) +
###   xlab("Round") +
###   ylab("Bundle Price") +
###   geom_line(data=lineDF, aes(round, value), color="violetred", size=1) 
### ggsave(sprintf("plots/XorPrices/pricetrajectorylargestVisB_%s.pdf",domain))
