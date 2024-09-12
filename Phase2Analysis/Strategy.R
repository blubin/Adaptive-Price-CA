source('common.R')

# Constants:
figs.dir = "plots/strategy/"
relevant.auctions.full <- c(
   'IBundle',
   'Linear Clock',
   'Linear Exact',
   'Linear Packing',
#    'Quadratic Exact',
#    'Quadratic Packing',
#    'HP Exact',
#    'HP Packing',
#    'Adaptive',
    'Adaptive(Min)',
    'Adaptive(Max)',
    'Adaptive(Abs)'
)

relevant.auctions.partial <- c(
   'IBundle',
   'Linear Clock',
   'Linear Exact',
   'Linear Packing',
#    'Quadratic Exact',
#    'Quadratic Packing',
#    'HP Exact',
#    'HP Packing',
    'Adaptive'
#    'Adaptive(Min)',
#    'Adaptive(Max)',
#    'Adaptive(Abs)'
)

relevant.auctions.names <-c("full",
                            "partial")
                                              
relevant.generators <- c("cats_arbitrary",
                         "cats_path",
                         "cats_reg")

generators.names <- list(qv="Quadratic",
                         cats_arbitrary="Arbitrary",
			                   cats_path="Paths",
			                   cats_reg="Regions")

relevant.num_items <- "30"

files.for.generator <- function(generator) { 
  # R doesn't have a hashmap ?!  So do this instead:
  if (generator == "cats_arbitrary")
    c("strategy/strategy_cats_arbitrary_epsilon_stepc_7_22_21.zip")
  else if (generator == "cats_path")
    c("strategy/strategy_cats_path_epsilon_stepc_7_22_21.zip")
  else if (generator == "cats_reg")
    c("strategy/strategy_cats_reg_epsilon_stepc_7_22_21.zip")
  else
    stop(paste('Unknown generator', generator))
}
path.for.generator <- function(generator) {
  # R doesn't have a hashmap ?!  So do this instead:
  if (generator == "cats_arbitrary")
    c("experiments/arb_epsilon_stepc_pool")
  else if (generator == "cats_path")
    c("experiments/strategy_cats_path_epsilon_stepc_pool")
  else if (generator == "cats_reg")
    c("experiments/strategy_cats_reg_epsilon_stepc_pool")
  else
    stop(paste('Unknown generator', generator))
}

read.data <- function(generator, relevant.auctions, relevant.auctions.name) {
  # Read all the files
  zipfiles <- files.for.generator(generator)
  zipfiles <- paste0('results/', zipfiles)
  pathsinfiles <- path.for.generator(generator)
  data.list <- mapply(read.instances.zip, zipfiles, pathsinfiles, SIMPLIFY=FALSE)
  # collapse to one big data set:
  data <- do.call("rbind.fill", data.list)
  # Munge Data:
  if ( relevant.auctions.name == "partial") {
     data$auction <- gsub("\\(Abs\\)", "", data$auction) # Drop the suffix
  }
  data$auction <- as.factor(data$auction)
  data$auction <- reorder(data$auction, new.order=relevant.auctions)
  data$epsilon <- reorder(data$epsilon)
  data <- filter(data, auction %in% relevant.auctions)
  data
}

stderror <- function(x) {
  return(sd(x)/sqrt(sum(!is.na(x))))
}

create.column.table <-function(column, strategy, heuristic_pool_num_, epsilon_hash, bold=TRUE, bold_max=TRUE, rounding_precision=1, table.placement="tb") {
  cat(sprintf('Creating table for %s-%s...\n', strategy,column))
  # Create one summary table:
  relevant.auctions.name <- "partial" # We are only going do the partial here.
  relevant.auctions <- get(paste0("relevant.auctions.",relevant.auctions.name))
  num_items = relevant.num_items #Only the relevant number of items
  outframe = as_tibble(data.frame())
  clearedframe = as_tibble(data.frame())
  for(generator in relevant.generators) {
    cat(sprintf(" Data for Generator %s...\n", generator))
    data <- read.data(generator, relevant.auctions, relevant.auctions.name)
    
    ### ADDED HERE:
    epsilon_ <- epsilon_hash(generator)
    data <- data %>% filter(bidding_strategy==strategy)
    data <- data %>% filter(epsilon == epsilon_)
    data <- data %>% filter(heuristic_pool_num==heuristic_pool_num_)
    ###

    data<- data %>% filter(items == num_items) 
    data.stepc.map <- pick.best.stepc(data, num_items)
    data.stepc <- data %>% inner_join(data.stepc.map, by=c("stepc", "auction"))
    data.stepc$stepc <- as.character(data.stepc$stepc)
    data.filtered <- data.stepc %>%
      #mutate(revenue_pct = (1-as.numeric(as.character(epsilon)))*100*final_revenue/efficient_value) %>%
      mutate(revenue_pct = 100*final_revenue/efficient_value) %>%
      mutate(stepc=ifelse(is.na(stepc), '-', as.character(stepc))) %>%
      group_by(auction, stepc) %>% 
      arrange(auction) %>%
      summarize_if(is.numeric, list(mean=mean, stderror=stderror)) #will create a column for each
    
    # Size of each experiment
    run_sizes <- data.stepc %>% 
      select(items, auction, epsilon, stepc) %>%
      filter(items == num_items) %>%
      filter(epsilon == epsilon_) %>%
      group_by(auction, stepc) %>% 
      summarize(run_size=n()) # Will add column for the number of entries in each group
    # Status counts for each experiment:
    status_counts <- data.stepc %>%  
      select(items, auction, epsilon, stepc, status) %>%
      filter(items == num_items) %>%
      filter(epsilon == epsilon_) %>%
      #truly_group_by(auction, stepc, status) %>% #Allows for 0 entries
      group_by(auction, stepc, status, .drop=FALSE) %>% #Allows for 0 entries
      summarize(status_count=n()) %>% # Will add column for the number of entries in each group
      inner_join(data.stepc.map %>% mutate(stepc=as.character(stepc)), by=c("stepc", "auction")) #Have to join again, cause truly gets all rows
    # Percent Cleared for each Experiment
    num_cleared <- status_counts %>%
      filter(status=="Cleared") %>%
      select(-status) %>% 
      rename(num_cleared=status_count) %>%
      inner_join(run_sizes, by=c("stepc", "auction")) %>%
      mutate(pct_cleared=100*num_cleared/run_size)
    # Modal status 
    modal_status <- status_counts %>%
      arrange(auction, status) %>%
      group_by(auction, stepc) %>%
      filter(status_count==max(status_count))%>%
      filter(row_number()==n()) %>%
      rename(modal_status_count=status_count)%>%
      rename(modal_status=status) %>%
      mutate(modal_status=recode(modal_status, "Personal Price"="Personal"))
    #Combine back:
    data.filtered <- data.filtered %>% 
      inner_join(num_cleared, by=c("auction")) %>%
      inner_join(modal_status, by=c("auction"))
    data.filtered$stepc <- as.factor(data.filtered$stepc)
      
    data.filtered <- data.filtered %>%
      select(auction, 
             rounds_mean, rounds_stderror, 
             runtime_mean, runtime_stderror, 
             final_price_degree_mean, final_price_degree_stderror,
             final_price_sparsity_mean, final_price_sparsity_stderror,
             efficiency_mean, efficiency_stderror,
             revenue_pct_mean, revenue_pct_stderror,
             pct_cleared, modal_status)             
    data.filtered<-replace.colnames(data.filtered, 
                                    c("rounds_mean", "rounds_stderror",
                                      "runtime_mean", "runtime_stderror", 
                                      "final_price_degree_mean", "final_price_degree_stderror",
                                      "final_price_sparsity_mean", "final_price_sparsity_stderror",
                                      "efficiency_mean", "efficiency_stderror",
                                      "revenue_pct_mean", "revenue_pct_stderror",
                                      "pct_cleared", "modal_status"),
                                    c("Rounds", "Rounds_stderror",
                                      "Runtime", "Runtime_stderror", 
                                      "Price Degree", "Price Degree_stderror",
                                      "Price Terms", "Price Terms_stderror",
                                      "Efficiency", "Efficiency_stderror", 
                                      "Revenue", "Revenue_stderror",
                                      "Percent Cleared", "Modal Status"))

    #Build the cleared version no matter what:
    data.cleared <- data.filtered %>% select(auction, "Percent Cleared", "Modal Status")
    data.cleared.transposed <- as_tibble(cbind(Metrics = names(data.cleared), t(data.cleared)), )
    names(data.cleared.transposed) <- make.unique(as.character(unlist(data.cleared.transposed[1,])))
    data.cleared.transposed <- data.cleared.transposed %>% rename(Metrics = auction) # because the previous line overwrites
    data.cleared.transposed <- data.cleared.transposed[-1,] #eliminate the row, now in the colnames
    data.cleared.transposed <- data.cleared.transposed %>% mutate(Generator=generators.names[[generator]]) %>% select(Generator, everything()) 
    clearedframe <- bind_rows(clearedframe, data.cleared.transposed)
    
    #Build everything else:
    if(column != "Percent Cleared") {
      data.filtered <- data.filtered %>% select(auction, column, paste0(column, "_stderror")) #Just the column we care about...
      data.transposed <- as_tibble(cbind(Metrics = names(data.filtered), t(data.filtered)))
      names(data.transposed) <- make.unique(as.character(unlist(data.transposed[1,])))
      data.transposed <- data.transposed %>% rename(Metrics = auction) # because the previous line overwrites
      data.transposed <- data.transposed[-1,] #eliminate the row, now in the colnames
      data.transposed <- data.transposed %>% mutate(Generator=generators.names[[generator]]) %>% select(Generator, everything()) 
      outframe <- bind_rows(outframe, data.transposed)
    }
  }

  #Ensure the Generator column has the right order:
  Generator_levels <- c("Arbitrary", "Paths", "Regions", "Quadratic", "Mean")
  clearedframe <- clearedframe %>% mutate(Generator = factor(Generator, levels = Generator_levels))
  if(column != "Percent Cleared") {
    outframe <- outframe %>% mutate(Generator = factor(Generator, levels = Generator_levels))
  }
  
  #Always prepare the clearing version:
  meanclearedframe <- clearedframe %>% filter(Metrics=="Percent Cleared") %>% select(-Metrics) 
  meanclearedframe <- meanclearedframe %>% arrange(Generator) %>% mutate_at(vars(-Generator), as.numeric)
  meanclearedframe <- bind_rows(meanclearedframe, bind_cols(Generator=factor("Mean", levels = Generator_levels), numcolwise(mean)(meanclearedframe)))
  meanclearedframe <- meanclearedframe %>% mutate_at(vars(-Generator), function(x){round(x,digits=rounding_precision)})
  stderrorclearedframe <- clearedframe %>% filter(Metrics=="Modal Status") %>% select(-Metrics) %>% arrange(Generator)
  stderrorclearedframe <- bind_rows(stderrorclearedframe, bind_cols(Generator=factor("Mean", levels = Generator_levels), add_row(slice(stderrorclearedframe, 0)%>%select(-Generator))))

  if(column == "Percent Cleared") {
    outframe <- clearedframe
    meanframe <- meanclearedframe
    stderrorframe <- stderrorclearedframe
    stderrorframe <- stderrorframe %>% # Make it smaller
      mutate_at(vars(-Generator),function(x)ifelse(is.na(x),NA,paste0('\\footnotesize{',x,'}')))
    postpend <- NULL
  } else {
    #Now do everything else:
    meanframe <- outframe %>% filter(Metrics==column) %>% select(-Metrics) 
    meanframe <- meanframe %>% arrange(Generator) %>% mutate_at(vars(-Generator), as.numeric)
    meanframe <- bind_rows(meanframe, bind_cols(Generator=factor("Mean", levels = Generator_levels), numcolwise(mean)(meanframe)))
    meanframe <- meanframe %>% mutate_at(vars(-Generator), function(x){round(x,digits=rounding_precision)})
    stderrorframe <- outframe %>% filter(Metrics==paste0(column, "_stderror")) %>% select(-Metrics) %>% arrange(Generator)
    stderrorframe <- stderrorframe %>% mutate_at(vars(-Generator), as.numeric)
    stderrorframe <- bind_rows(stderrorframe,  bind_cols(Generator=factor("Mean", levels = Generator_levels), add_row(slice(stderrorframe, 0)%>%select(-Generator))))
    stderrorframe <- stderrorframe %>% mutate_at(vars(-Generator), function(x){round(x,digits=rounding_precision)})
    postpend <- clearedframe %>% filter(Metrics=="Modal Status") %>% select(-Metrics) %>% arrange(Generator) %>%
      mutate_at(vars(-Generator),function(x)ifelse(x=="Cleared",NA,"$\\phantom{}^\\dagger$"))
    postpend <- postpend %>% mutate(across(everything(), as.character))
    postpend <- bind_rows(postpend, bind_cols(Generator=factor("Mean", levels = Generator_levels), add_row(slice(stderrorframe, 0)%>%select(-Generator))) %>% mutate(across(everything(), as.character)))
  }

  # cap <- paste0(column, " of the auctions for $\\epsilon=", 
  #               epsilon_hash('cats_arbitrary'), "$ for Arbitrary, $", 
  #               epsilon_hash('cats_path'), "$ for Paths, $", 
  #               epsilon_hash('cats_reg'), "$ for Regions, ", 
  #               " and $", num_items, "$ items. ")
  if(column == "Percent Cleared") {
    cap <- paste0("Percentage of auctions that cleared from the ", mean(run_sizes$run_size), " runs in each sample, for $\\epsilon=", epsilon_hash('cats_arbitrary'), "$ and $", num_items, "$ items, under heuristic bidding. The best value in each row is in bold.  The modal final state among these runs is provided in parenthesis.")
  } else if (column == "Rounds") {
    cap <- paste0("Number of auction rounds for $\\epsilon=",
    epsilon_hash('cats_arbitrary'), "$ and $", num_items, "$ items, under heuristic bidding.  The best value in each row is bold. Entries are the mean of $", mean(run_sizes$run_size), "$ runs with standard errors in parentheses.")
  } else if (column == "Price Degree") {
    cap <- paste0("Degree of prices in auctions for $\\epsilon=", epsilon_hash('cats_arbitrary'), "$ and $", num_items, "$ items. Entries are the mean of $", mean(run_sizes$run_size), "$ runs with standard errors in parentheses.")
  } else if (column == "Price Terms") {
    cap <- paste0("Number of price terms in auctions for $\\epsilon=", epsilon_hash('cats_arbitrary'), "$ and $", num_items, "$ items. Entries are the mean of $", mean(run_sizes$run_size), "$ runs with standard errors in parentheses.")
  } else {
    # Default
    cap <- paste0(column, " of the auctions for $\\epsilon=", 
                  epsilon_hash('cats_arbitrary'), "$ and $", 
                  num_items, "$ items, under heuristic bidding. ")
    if(bold){
      cap <- paste(cap,"The best value in each row is bold. ")
    }
    cap <- paste0(cap, "Entries are the mean of ",
    	               mean(run_sizes$run_size),
		       " runs with standard errors in parentheses.")
  }
  if(column != "Percent Cleared") {
    # Captions other than Percent Cleared can get the dagger.
    cap <- paste(cap,"A $\\dagger$ indicates less than half the instances cleared.")
  }
  cap <- paste0("\\label{fig:",strategy,".",gsub(" ","",column), "} ", cap)
  make.table(meanframe, paste0(strategy,"-",gsub(" ","",column)), "tables/strategy", cap, BRC=bold, BRC_each="row", BRC_max=bold_max,
             hline.after = c(-1,0,nrow(meanframe)-1,nrow(meanframe)),
             sanitize.text.func = function(x){x},
             stderrorframe=stderrorframe, stderrorframe_joincol="Generator", stderrorframe_round=rounding_precision,
             postpend=postpend, postpend_joincol="Generator",
             col_rename=c(Generator="Domain"),
	     table.placement=table.placement)
	     #align="ll|lllll"
}

# This block should run only if interactive mode
if(interactive()) {
  # Its purpose is to get the data and set variables for it:
  for(generator in relevant.generators) {
    strategy_summary <- frame()
    cat(sprintf("Reading Data for Generator %s...\n", generator))
    data <- read.data(generator, relevant.auctions.partial, 'partial')
    # treat each strategy separately
    for(strategy in c('default','heuristic')){
      # treat each pool level separately
      for(heuristic_pool_num_ in c(levels(data$heuristic_pool_num))) {
        # treat each epsilon separately
        for(epsilon_ in c(levels(data$epsilon))) {
          data.strat <- data %>% filter(bidding_strategy==strategy)
          data.strat <- data.strat %>% filter(items==relevant.num_items)
          data.strat <- data.strat %>% filter(epsilon==epsilon_)
          data.strat <- data.strat %>% filter(heuristic_pool_num==heuristic_pool_num_)
          
          data.strat.stepc.map <- pick.best.stepc(data.strat, num_items=relevant.num_items)
          data.strat.stepc <- data.strat %>% inner_join(data.strat.stepc.map, by=c("stepc", "auction"))
          
          strategy_summary <- rbind(strategy_summary, data.strat.stepc)
          
          #assign(paste0("data.",generator,".",strategy,".",epsilon_), data.strat)
          #assign(paste0("data.",generator,".",strategy,".",epsilon_,".stepc.map"), data.strat.stepc.map)
          #assign(paste0("data.",generator,".",strategy,".",epsilon_,".stepc"), data.strat.stepc)
          rm(data.strat, data.strat.stepc.map, data.strat.stepc)
        }
      }
    }
    rm(data)
    assign(paste0("strategy_summary.",generator), strategy_summary)
    rm(strategy_summary)
  }
}

# This block should only run in batch mode: it actually computes the files
# in interactive mode, we want to skip it:
if(!interactive()) { 
  heuristic_pool_num_ <- 2
  epsilon_hash <- function(generator) { 
    if (generator == "cats_arbitrary")
      return(.05)
    else if (generator == "cats_path")
      return(.05)#(1.2)
    else if (generator == "cats_reg")
      return(.05)
    else
      stop(paste('Unknown generator', generator))
  }
###   for(strategy_ in c('default','heuristic')){
  for(strategy_ in c('heuristic')){
    cat(sprintf("Writing strategy %s...\n", strategy_))
    create.column.table('Rounds', strategy_, heuristic_pool_num_, epsilon_hash, bold_max=FALSE, table.placement="H")
    create.column.table('Runtime', strategy_, heuristic_pool_num_, epsilon_hash, bold_max=FALSE, table.placement="H")
    create.column.table('Price Degree', strategy_, heuristic_pool_num_, epsilon_hash, bold=FALSE, table.placement="H")
    create.column.table('Price Terms', strategy_, heuristic_pool_num_, epsilon_hash, bold=FALSE, table.placement="H")
    create.column.table('Efficiency', strategy_, heuristic_pool_num_, epsilon_hash, table.placement="H")
    create.column.table('Revenue', strategy_, heuristic_pool_num_, epsilon_hash, bold=FALSE, table.placement="H")
    create.column.table('Percent Cleared', strategy_, heuristic_pool_num_, epsilon_hash, rounding_precision=0, table.placement="H")
  }
}
    
cat('Done.')
#options(warn=2, error=traceback)
#warnings()
