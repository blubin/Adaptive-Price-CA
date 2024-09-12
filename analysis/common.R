library(lattice, warn.conflicts = FALSE)
library(plyr, warn.conflicts = FALSE)
library(dplyr, warn.conflicts = FALSE)
library(xtable, warn.conflicts = FALSE)
library(DescTools, warn.conflicts = FALSE)
library(digest, warn.conflicts = FALSE)
library(feather, warn.conflicts = FALSE)
library(latexpdf, warn.conflicts = FALSE)
library(scales, warn.conflicts = FALSE)
library(tibble, warn.conflicts = FALSE)
library(R.methodsS3, warn.conflicts = FALSE, quietly=TRUE)
library(R.oo, warn.conflicts = FALSE, quietly=TRUE)
library(R.utils, warn.conflicts = FALSE, quietly=TRUE)
library(ggplot2, warn.conflicts = FALSE, quietly=TRUE)

source('monkey.R')
source('boldrowcol.R')

# try to prevent rPlots.pdf from being generated
pdf(NULL)

# Turn off xtable comments:
options(xtable.comment=FALSE)

figs.dir = "plots/"

##################
## Reading Data ##
##################

# Allocation Portion:
# What was Exact --> Exact
# What was Heuristic -> Packing

# Pricing:
# Linear
# Quadratic
# What was Adaptive --> HP [Heuristic Polynomial Price] (Omit, as we now present Adaptive)
# What was Cutting --> Adaptive [Polynomail Price]

# COMBOS:
# Linear Exact 
# Linear Packing 
# Adaptive (min, max, abs) [Packing] 
# Linear Clock
# IBundle

rename.auction <- function(auction)
{
  if (auction == 'AdaptiveHeuristicAuction') {
    return('HP Packing')
  } else if (auction == 'AdaptiveSubgradientAuction') {
    return('HP Exact')
  } else if (auction == 'LinearHeuristicAuction') {
    return('Linear Packing')
  } else if (auction == 'LinearSubgradientAuction') {
    return('Linear Exact')
  } else if (auction == 'QuadraticHeuristicAuction') {
    return('Quadratic Packing')
  } else if (auction == 'QuadraticSubgradientAuction') {
    return('Quadratic Exact')
  } else if (auction == 'IBundle') {
    return('IBundle')
  } else if (auction == 'LinearClockAuction') {
    return('Linear Clock')
  } else if (auction == 'AdaptiveCuttingAuction') {#Should have been called HeuristicCutting
    return('Adaptive')
  } else if (auction == 'AdaptiveCuttingAuction_min') {
    return('Adaptive(Min)')
  } else if (auction == 'AdaptiveCuttingAuction_max') {
    return('Adaptive(Max)')
  } else if (auction == 'AdaptiveCuttingAuction_abs') {
    return('Adaptive(Abs)')
  } else {
    stop(paste('Unknown auction', auction))
  }
}

rename.status <- function(status)
{
  if (status == 'Balance')
    'Cleared'
  else if (status == 'MaxIter')
    'Max Rounds'
  else if (status == 'MaxTime')
    'Max Time'
  else if (status == 'PersonalPriceRequired')
    'Personal Price'
  else if (status == 'UnderDemand')
    'Under Demand'
  else
    stop(paste('Unknown status', status))
}

replace.colnames <- function(df, old, new) {
  names(df) = lapply(names(df), function(x) if(x %in% old){new[match(x, old)]}else{x})
  return(df)
}

get.feather.fname <- function(fname, subdir) {
  return(paste0(gsub('.zip','',fname), '#', gsub('/',"_", subdir), '.feather'))
}

# We maintain a hash of the target file in fname.md5.  
# If hash matches, we return data from a cached version in .feather
get.cached <- function(fname, subdir) {
  if(!file.exists(fname)) {
    stop('File does not exist: ', fname)
  }
  fname_hash = paste(fname, '.md5', sep="")
  fname_feather = get.feather.fname(fname, subdir)
  if(!file.exists(fname_hash)) {
    message('Zip file new, creating cache for ', fname, ':', subdir)
    return(FALSE)
  }
  existing_hash = trimws(readChar(fname_hash, file.info(fname_hash)$size))
  current_hash = digest(fname, serialize=FALSE, file=TRUE)
  if(existing_hash != current_hash) {
    message('Zip file changed, refreshing cache for ', fname, ":", subdir)
    return(FALSE)
  }
  if(!file.exists(fname_feather)) {
    message('No existing cache file, creating cache for ', fname, ':', subdir)
    return(FALSE)
  }
  data = read_feather(fname_feather)
  return(data)
}

# Set up the cache data so it can be used in the future
set.cached <- function(fname, subdir, data) {
  if(!file.exists(fname)) {
    error('File does not exist', fname)
  }
  fname_hash = paste(fname, '.md5', sep="")
  fname_feather = get.feather.fname(fname, subdir)
  current_hash = digest(fname, serialize=FALSE, file=TRUE)
  cat(current_hash, file=fname_hash)
  write_feather(data, fname_feather)
}


# Read in instance files from a zip file 
read.instances.zip <- function(zipfile, subdir) {
  #message('Reading ', zipfile, ' in ', subdir)
  
  #First look to see if we have a cache:
  data = get.cached(zipfile, subdir)
  if(!is.logical(data)) {
    return(data)
  }
  # Get all files in the zip:
  ziplist <- unzip(zipfile, list=TRUE)$Name
  # Pull out only the instance summary files:
  instancefiles <- grep(paste0(subdir,'/instance#.*csv'), ziplist, value=TRUE)
  # Get the data
  data <- do.call(bind_rows, lapply(instancefiles, 
          function(x){d<-tryCatch(read.csv(unz(zipfile, x), stringsAsFactors=FALSE), error=function(e){warning(paste0("No data in: ", x));return(NULL)})
                      d$src <- paste0(zipfile, ':', subdir)
                      return(d)
            }))
  data$src <- as.factor(data$src)
  if (sum(is.na(data$auction))>0) {
    warning(paste0('NA in auction column: ', sum(is.na(data$auction))))
    data <- data[!is.na(data$auction),]
  }
  if("bidding_strategy" %in% colnames(data)){
    data$bidding_strategy <- as.factor(data$bidding_strategy) 
  }
  if("heuristic_pool_num" %in% colnames(data)){
    data$heuristic_pool_num <- as.factor(data$heuristic_pool_num) 
  }
  data$efficiency <- with(data, final_value / efficient_value)
  data$efficiency <- data$efficiency*100
  data$epsilon <- as.factor(data$epsilon)
  data$epsilon <- reorder(data$epsilon)
  data$epoch <- as.factor(data$epoch)
  data$epoch <- reorder(data$epoch)
  data$stepc <- as.factor(data$stepc)
  data$stepc <- reorder(data$stepc)
  data$items <- as.factor(data$items)
  data$items <- reorder(data$items)
  data$auction <- as.character(data$auction)
  data$generator_param_name <- as.factor(data$generator_param_name)
  data$generator_param_name <- reorder(data$generator_param_name)
  data$auction_class <- as.factor(data$auction_class)
  data$auction_class <- reorder(data$auction_class)
  if("expstrat" %in% colnames(data)) {
     data$auction <- ifelse(data$auction=="AdaptiveCuttingAuction",
                            paste(data$auction, data$expstrat, sep="_"),
                            data$auction)
     data$auction <- gsub("_NA", "", data$auction)#handle NA
  }
  data$auction <- sapply(data$auction, FUN=rename.auction)
  data$auction <- as.factor(data$auction)
  # Special Case the status for LCA:
  data$status <- as.character(data$status)
  data <- data %>% mutate(status=ifelse(auction=='Linear Clock' & status=='Balance', 'UnderDemand', status))
  data$status <- sapply(data$status, FUN=rename.status)
  data$status <- as.factor(data$status)
  set.cached(zipfile, subdir, data)
  return(data)
}

# Read in round files from a zip file 
# NOTE: NOT CURRENTLY CACHED
read.rounds.zip <- function(zipfile, subdir)
{
  # Get all files in the zip:
  ziplist <- unzip(zipfile, list=TRUE)$Name
  # Pull out only the instance summary files:
  instancefiles <- grep(paste0(subdir,'/round#.*csv'), ziplist, value=TRUE)
  # Get the data
  data = do.call(rbind, lapply(instancefiles, 
                               function(x){read.csv(unz(zipfile, x))}))
  data$epsilon <- as.factor(data$epsilon)
  data$epsilon <- reorder(data$epsilon)
  data$epoch <- as.factor(data$epoch)
  data$epoch <- reorder(data$epoch)
  data$stepc <- as.factor(data$stepc)
  data$stepc <- reorder(data$stepc)
  data$items <- as.factor(data$items)
  data$items <- reorder(data$items)
  data$auction <- as.character(data$auction)
  if("expstrat" %in% colnames(data)) {
    data$auction <- ifelse(data$auction=="AdaptiveCuttingAuction",
                           paste(data$auction, data$expstrat, sep="_"),
                           data$auction)
    data$auction <- gsub("_NA", "", data$auction)#handle NA
  }
  data$auction <- sapply(data$auction, FUN=rename.auction)
  data$auction <- as.factor(data$auction)
  data
}

####################
## Selection Data ##
####################

# Find the best stepc for each auction
# We pick this as the one that has the best efficiency.  
# Note: Assumes the Auction column is enough to ensure uniqueness.
# Note: IBundle will always return NA.  Careful to not drop it as a consequene.
pick.best.stepc.eff <- function(data, num_items) {
# Suppress "Factor `stepc` contains implicit NA, consider using `forcats::fct_explicit_na`" which is expected.
suppressWarnings( 
data %>% 
    filter(items==num_items) %>%
    select(auction, epsilon, stepc, efficiency) %>% 
    group_by(auction, epsilon, stepc) %>%
    summarize(median_eff = median(efficiency)) %>%
    group_by(auction) %>%
    filter(median_eff==max(median_eff)) %>%
    select(-epsilon) %>%
    filter(is.na(stepc) | (as.numeric(stepc)==min(as.numeric(stepc)))) %>%
    distinct(auction, stepc)
)
}

# Find the best stepc for each auction
# We pick this as the one that has the best efficiency.  
# Note: Assumes the Auction column is enough to ensure uniqueness.
# Note: IBundle will always return NA.  Careful to not drop it as a consequene.
pick.best.stepc.effPerRound <- function(data, num_items) {
  # Suppress "Factor `stepc` contains implicit NA, consider using `forcats::fct_explicit_na`" which is expected.
  suppressWarnings( 
    data %>% 
      filter(items==num_items) %>%
      select(auction, epsilon, stepc, efficiency, rounds) %>% 
      group_by(auction, epsilon, stepc) %>%
      summarize(median_effPerRound = median(efficiency/rounds)) %>%
      group_by(auction) %>%
      filter(median_effPerRound==max(median_effPerRound)) %>%
      select(-epsilon) %>%
      filter(is.na(stepc) | (as.numeric(stepc)==min(as.numeric(stepc)))) %>%
      distinct(auction, stepc)
  )
}

#pick.best.stepc <- pick.best.stepc.eff
pick.best.stepc <- pick.best.stepc.effPerRound

# Find the best epsilon&stepc pair for each auction
# We pick this as the one that has the best efficiency.  
# Note: Assumes the Auction column is enough to ensure uniqueness.
# Note: IBundle will always return NA.  Careful to not drop it as a consequene.
pick.best.epsilon_stepc <- function(data) {
data %>% 
    select(auction, epsilon, stepc, efficiency) %>% 
    group_by(auction, epsilon, stepc) %>%
    summarize(median_eff = median(efficiency)) %>%
    group_by(auction) %>%
    filter(median_eff==max(median_eff)) %>%
    filter(is.na(stepc) | (as.numeric(stepc)==min(as.numeric(stepc)))) %>%
    filter(as.numeric(epsilon)==min(as.numeric(epsilon))) %>%
    distinct(auction, epsilon, stepc)
}

# Create a table about the stepc chosen:
write.stepc.map <- function(stepc.map, file.name) {
  stepc.map <- arrange(stepc.map, auction)
  make.table(stepc.map, basename(file.name), dirname(file.name), "Best StepC by median efficiency.")
}

##################
## Table Output ##
##################

# Multi-row output in xtable, without needing kable
# See: https://stat.ethz.ch/pipermail/r-help/2010-July/247006.html
do.multirow<-function(df, which=1:ncol(df)){
  for(c in which){
    runs <- rle(as.character(df[,c]))
    if(all(runs$lengths>1)){
      tmp <- rep("", nrow(df))
      tmp[c(1, 1+head(cumsum(runs$lengths),-
                        1))] <-
        paste("\\multirow{",runs$lengths,"}{*}{",df[c(1,
                                                      1+head(cumsum(runs$lengths),-1)),c],"}",sep="")
      df[,c] <- tmp
    }
  }
  return(df)
}


make.table <- function(dataframe, filenamestem, outdir, caption=NULL, 
                       hline.after = getOption("xtable.hline.after", c(-1,0,nrow(dataframe))),
                       sanitize.text.func = getOption("xtable.sanitize.text.function", NULL),
                       multirow=FALSE,
                       BRC=FALSE, BRC_which=NULL, BRC_each="column", BRC_max=TRUE,
                       stderrorframe=NULL, stderrorframe_joincol=NULL, stderrorframe_round=NULL,
                       postpend=NULL, postpend_joincol=NULL,
                       align=NULL,
		       col_rename=NULL,
		       table.placement="tb",
		       rounding_precision=NULL) {
  # stderrorframe is a table of the same size and columns as dataframe. Every non-NA entry will be concatendated into correspondnig cell.
  if(multirow != FALSE) {
    if(multirow == TRUE) {
      dataframe <- do.multirow(dataframe)
    } else {
      dataframe <- do.multirow(dataframe, which=multirow)
    }
  }
  xtable <- xtable(dataframe, caption=caption, digits = rounding_precision)
  xtable <- autoformat(xtable)
  if (BRC) {
    xtable <- boldrowcol(xtable, which=BRC_which, each=BRC_each, max=BRC_max)
    sanitize.text.func = function(x){x}
  } else {
    # Running the table through boldrowcol will get us proper digit precision (i.e. X.0 or X.00) on the primary content (as opposed to the stderr which works anyway) even when we don't bold anything.  This is a hack, but it seems to work.
    xtable <- boldrowcol(xtable, which=matrix(FALSE, nrow=nrow(xtable),ncol=ncol(xtable)))
  }
  if(!is.null(stderrorframe)) {
    stderrorframe_joincol_name<-as.name(stderrorframe_joincol) #needed for dplyr v>=0.7 https://stackoverflow.com/questions/29678435/how-to-pass-dynamic-column-names-in-dplyr-into-custom-function
    for(c in names(xtable)) {# walk the columns
      if(c==stderrorframe_joincol){
        next()
      }
      c_name<-as.name(c)
      for(r in xtable[,stderrorframe_joincol]) { # walk the entries of the 'join' column
        # Find the existing and extra elements for this row/col
        cell <- xtable%>%filter(!!stderrorframe_joincol_name==r)%>%select(!!c_name)
        cellstderr <- stderrorframe%>%filter(!!stderrorframe_joincol_name==r)%>%select(!!c_name)
        #cat(paste(c,r,cell,cellstderr,"\n"))
        if(!is.na(cellstderr) ) {
          # if we have a value, format it, and concatenate it
          if(!is.null(stderrorframe_round) && suppressWarnings(!is.na(as.numeric(cellstderr)))) {
            cellstderr<-format(round(as.numeric(cellstderr), digits=stderrorframe_round), nsmall=stderrorframe_round)
            #cat(paste("Round",cellstderr,"\n"))
          }
          newcell <- paste0(cell, " (", cellstderr, ")")
          #cat(paste(newcell,"\n"))
          idx<-match(r, unlist(xtable[,stderrorframe_joincol]))
          xtable[idx,c]<-newcell
        }
      }
    }
  }

  if(!is.null(postpend)) {
    postpend_joincol_name<-as.name(postpend_joincol) #needed for dplyr v>=0.7 https://stackoverflow.com/questions/29678435/how-to-pass-dynamic-column-names-in-dplyr-into-custom-function
    for(c in names(xtable)) {# walk the columns
      if(c==postpend_joincol){
        next()
      }
      c_name<-as.name(c)
      for(r in xtable[,postpend_joincol]) { # walk the entries of the 'join' column
        # Find the existing and extra elements for this row/col
        cell <- xtable%>%filter(!!postpend_joincol_name==r)%>%select(!!c_name)
        cellpend <- postpend%>%filter(!!postpend_joincol_name==r)%>%select(!!c_name)
        #cat(paste(c,r,cell,cellpend,"\n"))
        if(!is.na(cellpend) ) {
          # if we have a value, concatenate it
          newcell <- paste0(cell, cellpend)
          #cat(paste(newcell,"\n"))
          idx<-match(r, unlist(xtable[,postpend_joincol]))
          xtable[idx,c]<-newcell
        }
      }
    }
  }
  if(!is.null(align)){
    align(xtable) <- align
  }

  if(!is.null(col_rename)){
    # col_rename should be of the form: c(oldcol="newcol", ...)
    for (old_name in names(col_rename)) {
      new_name <- col_rename[[old_name]]
      names(xtable) <- sub(old_name, new_name, names(xtable))
    }
  }
  
  tex_fname = file.path(outdir, paste0(filenamestem, '.tex'))
  tex_docfname = file.path(outdir, paste0(filenamestem, '_doc.tex'))
  mkdirs(outdir)
  print.xtable(xtable, booktabs=TRUE, include.rownames=FALSE,
               table.placement="tb",
               hline.after=hline.after,
               type = "latex",
               sanitize.text.function = sanitize.text.func,
               file=tex_docfname)

  #Create modified .tex file to include the lines needed for compiling the paper
  lines = readLines(tex_docfname)
  # tex2pdf can't handle float package H.  So only include any placement here
  if (table.placement != "tb") {
    lines[1] <- sub('tb', table.placement, lines[1])
  }
  lines <- append(lines, "\\tablesizing", after=1)
  lines <- append(lines, "\\SingleSpacedXI", after=1)
  writeLines(lines, tex_fname)

  #Now we are going to compare the existing hash with the newly created file.
  #If the hashes match, break.  Otherwise create a new hash and then proceed to make the pdf.
  current_hash = digest(tex_docfname, serialize=FALSE, file=TRUE)
  fname_hash = paste0(tex_fname, '.md5')
  if(file.exists(fname_hash)) {
    existing_hash = trimws(readChar(fname_hash, file.info(fname_hash)$size))
    if(existing_hash == current_hash) {
        return()
    }
  }
  cat(current_hash, file=fname_hash)
  
  # See: http://tex.stackexchange.com/questions/140796/generating-a-separate-pdf-file-of-tables-and-figures-from-a-latex-file
  #\usepackage[active,tightpage,floats]{preview}
  
  message('Creating: ', filenamestem, '_Doc.pdf')
  tex2pdf(file.path(outdir, paste0(filenamestem, '_Doc.tex')),
          dir=outdir,
          stem=filenamestem,
          clean=TRUE, onefile=TRUE, 
          preamble=makePreamble(morePreamble=c(command('usepackage', args="booktabs"),command('usepackage', options='active,tightpage,floats', args='preview'))),
          ignore.stdout=TRUE)
}

###################
## Plotting Data ##
###################

trellis.plot <- function(plotobj, file, textsize, pointsize=3, width=7, height=7)
{
  # file: name of the .pdf file.  We will infer the .eps name.
  # Do some trickery:  Write an EPS, which has no meta data.  
  # If that file is identical to existing file, stop
  # otherwise write a PDF too.
  existing_hash=""
  pdf_fname = paste0(figs.dir, file)
  eps_fname = gsub('.pdf', '.eps', pdf_fname)
  mkdirs(dirname(eps_fname))
  if(file.exists(eps_fname)) {
    existing_hash = digest(eps_fname, serialize=FALSE, file=TRUE)
    file.remove(eps_fname)
  }
  setEPS()
  trellis.device(device='postscript', file=eps_fname, width=width, height=height)
  plotobj <- update(plotobj, par.settings = list(fontsize = list(text = textsize, points = pointsize)))
  print(plotobj)
  dev.off()
  current_hash = digest(eps_fname, serialize=FALSE, file=TRUE)
  if(existing_hash != current_hash) {
    if(file.exists(pdf_fname)) {file.remove(pdf_fname)}
    trellis.device(device='pdf', file=pdf_fname, width=width, height=height)
    plotobj <- update(plotobj, par.settings = list(fontsize = list(text = textsize, points = pointsize)))
    print(plotobj)
    dev.off()
  }
}

ggsave.plot <- function(pdf_fname, ...) {
  # file: name of the .pdf file.  We will infer the .eps name.
  # Do some trickery:  Write an EPS, which has no meta data.  
  # If that file is identical to existing file, stop
  # otherwise write a PDF too.
  path=list(...)$path
  existing_hash=""
  eps_fname = gsub('.pdf', '.eps', pdf_fname)
  if(!is.null(path)){
    eps_fname<-paste0(path,'/',eps_fname)
  }
  mkdirs(dirname(eps_fname))
  if(file.exists(eps_fname)) {
    existing_hash = digest(eps_fname, serialize=FALSE, file=TRUE)
    file.remove(eps_fname)
  }
  ggsave(gsub('.pdf', '.eps', pdf_fname), ...)
  current_hash = digest(eps_fname, serialize=FALSE, file=TRUE)
  if(existing_hash != current_hash) {
    ggsave(pdf_fname, ...)
  }
}

make.clearing.info <- function(data, x.varied)
{
  data$varied <- data[[x.varied]]
  data %>%
    group_by(items, auction, varied, status) %>%
    summarise(count = n(),
              avg.rounds = mean(rounds),
              avg.eff = mean(efficiency),
              avg.winners = mean(final_num_winners)) %>%
    group_by(items, auction, varied) %>%
    mutate(percent = count / sum(count)) -> status.counts
  status.counts
}

clearing.plot <- function(results) {
  clearing.info <- make.clearing.info(results, 'epsilon')
  status.plot <- barchart(percent~varied | auction, groups=status,
                          data=clearing.info,
                          layout=c(length(unique(results$auction)),1),
                          xlab = expression(epsilon),
                          ylab='Percent',
                          auto.key=list(space='bottom'),
                          stack=TRUE,
                          scales = list(x=list(rot=45)))
  status.plot
}

# See: https://stackoverflow.com/questions/6461209/how-to-round-up-to-the-nearest-10-or-100-or-x
roundUpNice <- function(x, nice=4:40/4) {
    if(length(x) != 1) stop("'x' must be of length 1")
    10^floor(log10(x)) * nice[[which(x <= 10^floor(log10(x)) * nice)[[1]]]]
}

rounds.plot <- function(results, y.upper.bound=NULL, only_cleared=FALSE) {
  if (only_cleared) 
    #results <- subset(results, status == 'Cleared' | auction == 'IBundle')    
    results <- subset(results, status == 'Cleared')
  if (is.null(y.upper.bound)) {
     m <- max(results$rounds)
     n <- roundUpNice(m)
     if (m/n > .95)
        y.upper.bound <- n*1.05
     else
        y.upper.bound <- n
  }
  tmp.plot <- bwplot(rounds~epsilon | auction,
                        data=results,
                        layout=c(length(unique(results$auction)),1),
                        ylim=c(0, y.upper.bound),
                        xlab=expression(epsilon),
                        ylab='Rounds',
                        scales = list(x=list(rot=45)))
  tmp.plot
}

eff.plot <- function(results, only_cleared=FALSE) {
  if (only_cleared) 
    results <- subset(results, status == 'Cleared')
  tmp.plot <- bwplot(efficiency~epsilon | auction,
                     data=results,
                     layout=c(length(unique(results$auction)),1),
                     xlab=expression(epsilon),
                     ylab="Efficiency",
                     scales = list(x=list(rot=45)))
  tmp.plot
}

