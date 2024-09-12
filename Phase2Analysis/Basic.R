source('common.R')
library(tidyr)

# Constants:
figs.dir = "plots/basic/"
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
                                              
relevant.generators <- c("qv",
                         "cats_arbitrary",
                         "cats_path",
                         "cats_reg")

generators.names <- list(qv="Quadratic",
                         cats_arbitrary="Arbitrary",
			                   cats_path="Paths",
			                   cats_reg="Regions")

relevant.num_items <- c("10", "30")

relevant.table.epsilon <- 0.05

files.for.generator <- function(generator) { 
  # R doesn't have a hashmap ?!  So do this instead:
  if (generator == "qv") 
    c(#"basic/basic_qv_epsilon_stepc_10_5_21.zip",
      "basic/basic_qv_epsilon_stepc_1_25_22.zip",
      #"lca/lca_epsilon_stepc_7_30_19.zip",
      "lca/lca_epsilon_stepc_9_14_21.zip",
#      "cutting/cutting_min_epsilon_stepc_7_31_18.zip",
#      "cutting/cutting_max_epsilon_stepc_8_3_18.zip",
      #"cutting/cutting_abs_epsilon_stepc_04_29_20.zip")
      "cutting/cutting_abs_epsilon_stepc_9_7_21.zip")
#      "cutting/cutting20_abs_epsilon_stepc_05_20_20.zip") 
  else if (generator == "cats_arbitrary")
    c(#"basic/basic_cats_arbitrary_epsilon_stepc_10_5_21.zip",
      "basic/basic_cats_arbitrary_epsilon_stepc_1_25_22.zip",
      #"lca/lca_epsilon_stepc_7_30_19.zip",
      "lca/lca_epsilon_stepc_9_14_21.zip",
      #      "cutting/cutting_min_epsilon_stepc_7_31_18.zip",
#      "cutting/cutting_max_epsilon_stepc_8_3_18.zip",
      #"cutting/cutting_abs_epsilon_stepc_04_29_20.zip")
      "cutting/cutting_abs_epsilon_stepc_9_7_21.zip")
#       "cutting/cutting20_abs_epsilon_stepc_05_20_20.zip") 
  else if (generator == "cats_path")
    c(#"basic/basic_cats_path_epsilon_stepc_10_5_21.zip",
      "basic/basic_cats_path_epsilon_stepc_1_25_22.zip",
      #"lca/lca_epsilon_stepc_7_30_19.zip",
      "lca/lca_epsilon_stepc_9_14_21.zip",
#      "cutting/cutting_min_epsilon_stepc_7_31_18.zip",
#      "cutting/cutting_max_epsilon_stepc_8_3_18.zip",
      #"cutting/cutting_abs_epsilon_stepc_04_29_20.zip")
      "cutting/cutting_abs_epsilon_stepc_9_7_21.zip")
#       "cutting/cutting20_abs_epsilon_stepc_05_20_20.zip") 
  else if (generator == "cats_reg")
    c(#"basic/basic_cats_reg_epsilon_stepc_10_5_21.zip",
      "basic/basic_cats_reg_epsilon_stepc_1_25_22.zip",
      #"lca/lca_epsilon_stepc_7_30_19.zip",
      "lca/lca_epsilon_stepc_9_14_21.zip",
#      "cutting/cutting_min_epsilon_stepc_7_31_18.zip",
#      "cutting/cutting_max_epsilon_stepc_8_3_18.zip",
      #"cutting/cutting_abs_epsilon_stepc_04_29_20.zip")
      "cutting/cutting_abs_epsilon_stepc_9_7_21.zip")
#       "cutting/cutting20_abs_epsilon_stepc_05_20_20.zip") 
  else
    stop(paste('Unknown generator', generator))
}
path.for.generator <- function(generator) {
  # R doesn't have a hashmap ?!  So do this instead:
  if (generator == "qv")
    c("experiments/basic_qv_epsilon_stepc",
      "experiments/lca/lca_qv_epsilon_stepc",
#      "experiments/cutting_min/cutting_qv_epsilon_stepc",
#      "experiments/cutting_max/cutting_qv_epsilon_stepc",
      "experiments/cutting_abs/cutting_qv_epsilon_stepc")
#       "experiments/cutting20_abs/cutting20_qv_epsilon_stepc")
else if (generator == "cats_arbitrary")
    c("experiments/basic_cats_arbitrary_epsilon_stepc",
      "experiments/lca/lca_cats_arbitrary_epsilon_stepc",
#      "experiments/cutting_min/cutting_cats_arbitrary_epsilon_stepc",
#      "experiments/cutting_max/cutting_cats_arbitrary_epsilon_stepc",
      "experiments/cutting_abs/cutting_cats_arbitrary_epsilon_stepc")
#       "experiments/cutting20_abs/cutting20_cats_arbitrary_epsilon_stepc")
  else if (generator == "cats_path")
    c("experiments/basic_cats_path_epsilon_stepc",
      "experiments/lca/lca_cats_path_epsilon_stepc",
#      "experiments/cutting_min/cutting_cats_path_epsilon_stepc",
#      "experiments/cutting_max/cutting_cats_path_epsilon_stepc",
      "experiments/cutting_abs/cutting_cats_path_epsilon_stepc")
#       "experiments/cutting20_abs/cutting20_cats_path_epsilon_stepc")
else if (generator == "cats_reg")
    c("experiments/basic_cats_reg_epsilon_stepc",
      "experiments/lca/lca_cats_reg_epsilon_stepc",
#      "experiments/cutting_min/cutting_cats_reg_epsilon_stepc",
#      "experiments/cutting_max/cutting_cats_reg_epsilon_stepc",
      "experiments/cutting_abs/cutting_cats_reg_epsilon_stepc")
#       "experiments/cutting20_abs/cutting20_cats_reg_epsilon_stepc")
else
    stop(paste('Unknown generator', generator))
}

read.data <- function(generator, relevant.auctions, relevant.auctions.name) {
  # Read all the files
  zipfiles <- files.for.generator(generator)
  zipfiles <- paste0('results/', zipfiles)
  pathsinfiles <- path.for.generator(generator)
  data.list <- mapply(read.instances.zip, zipfiles, pathsinfiles)
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

create.table <- function(data.stepc, generator, relevant.auctions.name, relevant.table.epsilon) {
  for (num_items in relevant.num_items) {
    # Create a table:
    data.table <- select(data.stepc, items, auction, epsilon, stepc, rounds, runtime,
                         final_price_degree, final_price_sparsity, final_revenue,
              	         efficiency) %>%
      filter(items == num_items) %>%
      filter(epsilon == relevant.table.epsilon) %>%
      mutate(stepc=ifelse(is.na(stepc), '-', as.character(stepc))) %>%
      group_by(auction, stepc) %>% 
      summarize_if(is.numeric, mean) %>%
      arrange(auction) %>%
      mutate(rounds=round(rounds,0)) %>%
      mutate(rounds=ifelse(rounds==1000, 'Max', as.character(rounds))) %>%
      mutate(runtime=round(runtime,0)) %>%
      mutate(final_price_degree=round(final_price_degree,1)) %>%
      mutate(final_price_sparsity=round(final_price_sparsity,1)) %>%
      mutate(final_revenue=dollar(final_revenue)) %>%
      mutate(efficiency=round(efficiency,1))  
    size <- select(data.stepc, items, auction, epsilon, stepc, rounds, runtime,
                   final_price_degree, final_price_sparsity, final_revenue,
                   efficiency) %>%
      filter(items == num_items) %>%
      filter(epsilon == relevant.table.epsilon) %>%
      select(-epsilon) %>%
      mutate(stepc=ifelse(is.na(stepc), '-', as.character(stepc))) %>%
      group_by(auction, stepc) %>% 
      count()
    size <- mean(size$n)
    
    names(data.table) <- c("Auction", "StepC", "Rounds", "Run Time", "Price Degree", "Price Terms", "Revenue", "Efficiency")
    filenamestem <- sprintf('Basic_%s_%s_%s', generator, num_items, relevant.auctions.name)
    cap <- paste0("Properties of the auctions for $\\epsilon=", relevant.table.epsilon, "$ and $",
                  num_items, "$ items in the ", generators.names[[generator]], " domain.",
                  " The StepC resulting in the best median efficiency is presented. ",
                  " Rows represent the mean of ", size, " runs.")
    make.table(data.table, filenamestem, "tables/basic", cap)
  }
}

create.plots <- function(data, generator, relevant.auctions.name) {
  for (num_items in relevant.num_items) {
    data.items <- filter(data, items == num_items)
    # Clearing Plot:
    clearing.plot <- clearing.plot(data.items)
    trellis.plot(clearing.plot, sprintf("%s/Basic_%s_%s_%s_Clearing.pdf", generator, generator, num_items, relevant.auctions.name), textsize=9, height=4)
    # Rounds Plot:    
    rounds.plot <- rounds.plot(data.items)
    trellis.plot(rounds.plot, sprintf("%s/Basic_%s_%s_%s_Rounds.pdf", generator, generator, num_items, relevant.auctions.name), textsize=9, height=4)
    # Efficiency Plot:
    eff.plot <- eff.plot(data.items)
    trellis.plot(eff.plot, sprintf("%s/Basic_%s_%s_%s_Efficiency.pdf", generator, generator, num_items, relevant.auctions.name), textsize=9, height=4)
  }
}

create.summary.table <-function(rounding_precision=1) {
  # Create one summary table:
  relevant.auctions.name <- "partial" # We are only goting do the partial here.
  relevant.auctions <- get(paste0("relevant.auctions.",relevant.auctions.name))
  num_items = 30
  summary = as_tibble(data.frame())
  for(generator in relevant.generators) {
    cat(sprintf("Analyzing Data for Generator %s...\n", generator))
    data <- read.data(generator, relevant.auctions, relevant.auctions.name)
    data.stepc.map <- pick.best.stepc(data, num_items)
    data.stepc <- data %>% inner_join(data.stepc.map, by=c("stepc", "auction"))
    data.filtered <- data.stepc %>% 
      filter(items == num_items) %>%
      filter(epsilon == relevant.table.epsilon) %>%
      mutate(stepc=ifelse(is.na(stepc), '-', as.character(stepc))) %>%
      group_by(auction, stepc) %>% 
      summarize_if(is.numeric, mean) %>%
      arrange(auction) %>%
      mutate(rounds=ifelse(rounds==1000, 'Max', as.character(round(rounds,0)))) %>%
      mutate(runtime=round(runtime,digits=0)) %>%
      mutate(final_price_degree=round(final_price_degree, digits=rounding_precision)) %>%
      mutate(final_price_sparsity=round(final_price_sparsity,digits=rounding_precision)) %>%
      mutate(final_revenue=dollar(final_revenue)) %>%
      mutate(efficiency=round(efficiency,digits=rounding_precision))%>%
      select(auction, rounds, runtime, final_price_degree, final_price_sparsity,efficiency, final_revenue)
    data.filtered<-replace.colnames(data.filtered, c("rounds","runtime", "final_price_degree", "final_price_sparsity", "efficiency", "final_revenue"), 
                                    c("Rounds",'Runtime', "Price Degree", "Price Terms","Efficiency", "Revenue"))
    
    data.transposed <- as_tibble(cbind(Metrics = names(data.filtered), t(data.filtered)))
    names(data.transposed) <- as.character(unlist(data.transposed[1,]))
    data.transposed <- data.transposed %>% rename(Metrics = auction) # because the previous line overwrites
    data.transposed <- data.transposed[-1,] #eliminate the row, now in the colnames
    data.transposed <- data.transposed %>% mutate(Generator=generators.names[[generator]]) %>%
      select(Metrics, Generator, everything()) 
    summary <- bind_rows(summary, data.transposed)
  }
  summary <- summary %>% arrange(Metrics)
  
  make.table(summary, "BasicSummary", "tables/basic", "Summary of Auction results.")
}

stderror <- function(x) {
  return(sd(x)/sqrt(sum(!is.na(x))))
}

create.column.table <-function(column, bold=TRUE, bold_max=TRUE, rounding_precision=1) {
  cat(sprintf('Creating table for %s...\n', column))
  # Create one summary table:
  relevant.auctions.name <- "partial" # We are only goting do the partial here.
  relevant.auctions <- get(paste0("relevant.auctions.",relevant.auctions.name))
  num_items = 30 #Only the 30 item data
  outframe = as_tibble(data.frame())
  clearedframe = as_tibble(data.frame())
  for(generator in relevant.generators) {
    cat(sprintf(" Data for Generator %s...\n", generator))
    data <- read.data(generator, relevant.auctions, relevant.auctions.name)
    data.stepc.map <- pick.best.stepc(data, num_items)
    data.stepc <- data %>% inner_join(data.stepc.map, by=c("stepc", "auction"))
    data.stepc$stepc <- as.character(data.stepc$stepc)
    data.filtered <- data.stepc %>%
      mutate(revenue_pct = (1-as.numeric(as.character(epsilon)))*100*final_revenue/efficient_value) %>%
      mutate(stepc=ifelse(is.na(stepc), '-', as.character(stepc))) %>%
      filter(items == num_items) %>%
      filter(epsilon == relevant.table.epsilon) %>%
      group_by(auction, stepc) %>% 
      arrange(auction) %>%
      summarize_if(is.numeric, list(mean=mean, stderror=stderror)) #will create a column for each
    
    # Size of each experiment
    run_sizes <- data.stepc %>% 
      select(items, auction, epsilon, stepc) %>%
      filter(items == num_items) %>%
      filter(epsilon == relevant.table.epsilon) %>%
      group_by(auction, stepc) %>% 
      summarize(run_size=n()) # Will add column for the number of entries in each group
    # Status counts for each experiment:
    status_counts <- data.stepc %>%  
      select(items, auction, epsilon, stepc, status) %>%
      filter(items == num_items) %>%
      filter(epsilon == relevant.table.epsilon) %>%
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

  # Some captions are special-cased. The rest get the default caption
  if(column == "Percent Cleared") {
    cap <- paste0("Percentage of auctions that cleared from the ", mean(run_sizes$run_size), " runs in each sample.  The modal final state among these runs is provided in parenthesis.")
  } else if(column == "Rounds") {
    cap <- paste0("Number of auction rounds for $\\epsilon=", relevant.table.epsilon, "$ and $", num_items, "$ items.  The best value in each row is bold. Entries are the mean of $", mean(run_sizes$run_size), "$ runs with standard errors in parentheses.")
  } else {
    # default caption:
    cap <- paste0(column, " of the auctions for $\\epsilon=", relevant.table.epsilon, "$ and $", num_items, "$ items. ")
    if(bold){
      cap <- paste(cap,"The best value in each row is bold. ")
    }
    cap <- paste0(cap, "Entries are the mean of ", mean(run_sizes$run_size), " runs with standard errors in parentheses.")
  }
  if(column != "Percent Cleared") {
    # Captions other than percent cleared can get the dagger.
    cap <- paste(cap,"A $\\dagger$ indicates less than half the instances cleared.")
  }
  cap <- paste0("\\label{fig:", gsub(" ","",column), "} ", cap)
  make.table(meanframe, gsub(" ","",column), "tables/basic", cap, BRC=bold, BRC_each="row", BRC_max=bold_max,
             hline.after = c(-1,0,nrow(meanframe)-1,nrow(meanframe)),
             sanitize.text.func = function(x){x},
             stderrorframe=stderrorframe, stderrorframe_joincol="Generator", stderrorframe_round=rounding_precision,
             postpend=postpend, postpend_joincol="Generator",
             align="ll|lllll", col_rename=c(Generator="Domain"),
	     rounding_precision=rounding_precision)
}

create.price_degree.plot <-function() {
  cat('Creating Price Degree plot\n')
  # Create one summary table:
  relevant.auctions.name <- "partial" # We are only goting do the partial here.
  relevant.auctions <- get(paste0("relevant.auctions.",relevant.auctions.name))
  num_items = 30 #Only the 30 item data
  outframe = as_tibble(data.frame())
  for(generator in relevant.generators) {
    cat(sprintf(" Data for Generator %s...\n", generator))
    data <- read.data(generator, relevant.auctions, relevant.auctions.name)
    data.stepc.map <- pick.best.stepc(data, num_items)
    data.stepc <- data %>% inner_join(data.stepc.map, by=c("stepc", "auction"))
    data.stepc$stepc <- as.character(data.stepc$stepc)
    data.filtered <- data.stepc %>%
      mutate(stepc=ifelse(is.na(stepc), '-', as.character(stepc))) %>%
      filter(items == num_items) %>%
      filter(epsilon == relevant.table.epsilon) %>%
      filter(auction == "Adaptive") %>%
      add_column(Generator=generators.names[[generator]]) %>%
      select(Generator, final_price_degree)   
      outframe <- bind_rows(outframe, data.filtered)
  }
  
  outframe <- outframe %>%
    mutate(Generator = factor(Generator, levels = c("Arbitrary", "Paths", "Regions", "Quadratic")))

  make.table(outframe %>% summarize(mean=mean(final_price_degree)), "PriceDegreeMean","tables/basic")
  
  ggplot(outframe, aes(x=Generator, y=final_price_degree))+geom_boxplot()+xlab("")+ylab("Price Degree")
  ggsave.plot("PriceDegreeBox.pdf", path="plots/basic", width=3.5, height=2.5, scale=1.33)

  # Size of each experiment
  run_sizes <- data.stepc %>% 
    select(items, auction, epsilon, stepc) %>%
    filter(items == num_items) %>%
    filter(epsilon == relevant.table.epsilon) %>%
    group_by(auction, stepc) %>% 
    summarize(run_size=n()) # Will add column for the number of entries in each group
  
  cap <- paste0("Box plot showing the distribution of the degree of the final prices in the Adaptive auction with ",
                "$\\epsilon=", relevant.table.epsilon, "$ and $", num_items, "$ items.  Each box represents $", mean(run_sizes$run_size),
                "$ samples from the domain.")
  cap <- paste0("\\label{fig:PriceDegreeBox}", cap)
  cat(cap, file="plots/basic/PriceDegreeBox_caption.tex")
}

create.price_terms.plot <-function(personThresh=1000) {
  # Create a boxwiskers plot for Price Terms with IBundle and Adaptive and a line where 30 is, grouped by distribution
  # NOTE: we drop points above personThresh and plot these separately to avoid messing up the scale.
  cat('Creating Price Terms plot\n')
  # Create one summary table:
  relevant.auctions.name <- "partial" # We are only goting do the partial here.
  relevant.auctions <- get(paste0("relevant.auctions.",relevant.auctions.name))
  num_items = 30 #Only the 30 item data
  outframe = as_tibble(data.frame())
  for(generator in relevant.generators) {
    cat(sprintf(" Data for Generator %s...\n", generator))
    data <- read.data(generator, relevant.auctions, relevant.auctions.name)
    data.stepc.map <- pick.best.stepc(data, num_items)
    data.stepc <- data %>% inner_join(data.stepc.map, by=c("stepc", "auction"))
    data.stepc$stepc <- as.character(data.stepc$stepc)
    data.filtered <- data.stepc %>%
      #mutate(final_price_sparsity=ifelse(final_price_sparsity<=personThresh,final_price_sparsity,final_price_sparsity/agents))%>%      
      #mutate(final_price_sparsity=ifelse(auction=="IBundle",final_price_sparsity/agents,final_price_sparsity))%>%
      filter(final_price_sparsity<=personThresh) %>%
      mutate(stepc=ifelse(is.na(stepc), '-', as.character(stepc))) %>%
      filter(items == num_items) %>%
      filter(epsilon == relevant.table.epsilon) %>%
      filter(auction %in% c("Adaptive","IBundle")) %>%
      add_column(Generator=generators.names[[generator]]) %>%
      filter(!(auction=="IBundle" & Generator=="Quadratic")) %>% #drop the IBundle/Quadratic point because its an outlier
      select(Generator, auction, final_price_sparsity)   
    outframe <- bind_rows(outframe, data.filtered)
  }
  
  outframe <- outframe %>%
    mutate(Generator = factor(Generator, levels = c("Arbitrary", "Paths", "Regions", "Quadratic")))
  
  ggplot(outframe, aes(x=Generator, y=final_price_sparsity, fill=auction))+
    geom_boxplot(position = position_dodge2(preserve = "single"))+
    theme(legend.position="bottom")+theme(legend.title=element_blank())+theme(legend.margin=margin(c(-20,0,0,0)))+
    xlab("")+
    ylab("Price Terms")
  ggsave.plot("PriceTermsBox.pdf", path="plots/basic", width=3.5, height=2.5, scale=1.33)

  # Size of each experiment
  run_sizes <- data.stepc %>% 
    select(items, auction, epsilon, stepc) %>%
    filter(items == num_items) %>%
    filter(epsilon == relevant.table.epsilon) %>%
    group_by(auction, stepc) %>% 
    summarize(run_size=n()) # Will add column for the number of entries in each group
  
### cap <- paste0("Box plot showing the distribution of the number of terms in the prices of IBundle and the Adaptive auctions (the others are linearly priced) with ",
###               "$\\epsilon=", relevant.table.epsilon, "$. ",
###               "IBundle fails to clear instances in the Quadratic domain, and we therefore omit this data point. ",
###               "Each box represents $", mean(run_sizes$run_size),
###               "$ samples in a domain with $", num_items, "$ goods.")

###  cap <- paste0("Box plot showing the distribution of the number of terms in the anonymous prices used by the IBundle and Adaptive auctions. IBundle fails to clear instances in the Quadratic domain, and we therefore omit this data point.  Each box represents ", mean(run_sizes$run_size), " samples.")
  cap <- paste0("Box plot showing the distribution of the number of terms in final anonymous prices in the Adaptive auction and final prices in \\ibundle. \\ibundle fails to clear instances in the Quadratic domain, and we therefore omit this data point.")

  cap <- paste0("\\label{fig:PriceTermsBox}", cap)
  cat(cap, file="plots/basic/PriceTermsBox_caption.tex")
}

create.price_terms_personalized.plot <-function(personThresh=1000) {
  # Create a boxwiskers plot for Price Terms for Adaptive and Paths
  # specifically for the personalized points (i.e. those above personThresh)
  # NOTE: we look only at points above personThresh and plot these for 
  # these separately to avoid messing up the scale.
  cat('Creating Price Terms Personalized plot\n')
  # Create one summary table:
  relevant.auctions.name <- "partial" # We are only going do the partial here.
  relevant.auctions <- get(paste0("relevant.auctions.",relevant.auctions.name))
  num_items <- 30 #Only the 30 item data
  generator <- "cats_path"
  outframe <- as_tibble(data.frame())
  cat(sprintf(" Data for Generator %s...\n", generator))
  data <- read.data(generator, relevant.auctions, relevant.auctions.name)
  data.stepc.map <- pick.best.stepc(data, num_items)
  data.stepc <- data %>% inner_join(data.stepc.map, by=c("stepc", "auction"))
  data.stepc$stepc <- as.character(data.stepc$stepc)
  data.filtered <- data.stepc %>%
    filter(final_price_sparsity>personThresh) %>%
    mutate(final_price_sparsity = final_price_sparsity/agents) %>%
    mutate(stepc=ifelse(is.na(stepc), '-', as.character(stepc))) %>%
    filter(items == num_items) %>%
    filter(epsilon == relevant.table.epsilon) %>%
    filter(auction %in% c("Adaptive")) %>%
    add_column(Generator=generators.names[[generator]]) %>%
    select(Generator, auction, final_price_sparsity)   
  outframe <- bind_rows(outframe, data.filtered)
  outframe <- outframe %>%
    mutate(Generator = factor(Generator, levels = c("Arbitrary", "Paths", "Regions", "Quadratic")))
  
  ggplot(outframe, aes(x=Generator, y=final_price_sparsity, fill=auction))+
    geom_boxplot(width=0.5, fill="#00bfc4",
                 position = position_dodge2(preserve = "single"))+
    ylim(30,160)+
    theme(legend.position="bottom")+theme(legend.title=element_blank())+theme(legend.margin=margin(c(-20,0,0,0)))+
    xlab("")+
    ylab("Price Terms per Agent")
  ggsave.plot("PriceTermsPersonalizedBox.pdf", path="plots/basic", width=3.5, height=2.5, scale=1.33)
  
  # Number of such points
  personalized_size <- nrow(outframe)
  
  # Size of each experiment
  run_sizes <- data.stepc %>% 
    select(items, auction, epsilon, stepc) %>%
    filter(items == num_items) %>%
    filter(epsilon == relevant.table.epsilon) %>%
    group_by(auction, stepc) %>% 
    summarize(run_size=n()) # Will add column for the number of entries in each group
  
### cap <- paste0("Box plot showing the distribution of the number of terms per agent in the prices of Adaptive auctions that employ personalized prices and where",
###               "$\\epsilon=", relevant.table.epsilon, "$. ",
###               "There are $", personalized_size, "$ such instances among the $", mean(run_sizes$run_size),
###               "$ samples from a domain with $", num_items, "$ goods.")

###  cap <- paste0("Box plot showing the distribution of the number of terms per bidder in the prices of Adaptive auctions that employ personalized prices and where $\\epsilon=", relevant.table.epsilon, "$. There are $\\numPersonalizedInPaths$ such instances among the $", mean(run_sizes$run_size), "$ samples from the Path domain with $", num_items, "$ goods.")
  cap <- paste0("Box plot showing the distribution of the number of terms per bidder for the instances where the Adaptive auction switches to personalized prices. There are $\\numPersonalizedInPaths$ such instances among the $", mean(run_sizes$run_size), "$ samples from the Paths domain with $", num_items, "$ goods and $\\epsilon=", relevant.table.epsilon, "$.")

  cap <- paste0("\\label{fig:PriceTermsPersonalizedBox}", cap)
  cat(cap, file="plots/basic/PriceTermsPersonalizedBox_caption.tex")
}
create.price_terms_personalized.plot()

create.stepc_map.table<- function() {
  relevant.auctions.name <- "partial" # We are only going do the partial here.
  relevant.auctions <- get(paste0("relevant.auctions.",relevant.auctions.name))
  num_items <- 30 #Only the 30 item data
  outframe = as_tibble(data.frame())
  for(generator in relevant.generators) {
    cat(sprintf("Analyzing Data for Generator %s...\n", generator))
    cat(sprintf("Analyzing Auction Set %s...\n", relevant.auctions.name))
    data <- read.data(generator, relevant.auctions, relevant.auctions.name)
    #Pick the best stepc for each auction:
    data.stepc.map <- pick.best.stepc(data, num_items=num_items)
    data.stepc.map <- data.stepc.map %>% mutate(generator=generator)
    outframe <- bind_rows(outframe, data.stepc.map)
  }
  outframe <- outframe %>% filter(auction!="IBundle")
  outframe <- outframe %>% mutate(Generator=recode(generator, 
                                       'qv'=generators.names[['qv']],
                                       'cats_arbitrary'=generators.names[['cats_arbitrary']],
                                       'cats_reg'=generators.names[['cats_reg']],
                                       'cats_path'=generators.names[['cats_path']])) %>% select(-generator)
  
  outframe <- outframe %>% pivot_wider(names_from=auction,values_from=stepc)
  outframe <- outframe %>%
    mutate(Generator = factor(Generator, levels = c("Arbitrary", "Paths", "Regions", "Quadratic")))
  outframe <- outframe %>% arrange(Generator)
  cap <- paste0("The $c$ parameter used in determining the step size in each auction.  For each experimental setup, we report using the value of $c$ that results in the greatest median efficiency over the samples in the experiment.")
  cap <- paste0("\\label{tab:StepCMap} ", cap)
  make.table(outframe, "StepCMap","tables/basic",cap, col_rename=c(Generator="Domain"), table.placement="H")
}

# This block should only run in batch mode: it actually computes the files
# in interactive mode, we want to skip it:
if(!interactive()) { 
###   # # First version of output, split into many files:
###   for(generator in relevant.generators) {
###     cat(sprintf("Analyzing Data for Generator %s...\n", generator))
###     for(relevant.auctions.name in relevant.auctions.names) {
###       cat(sprintf("Analyzing Auction Set %s...\n", relevant.auctions.name))
###       relevant.auctions <- get(paste0("relevant.auctions.",relevant.auctions.name))
###       data <- read.data(generator, relevant.auctions, relevant.auctions.name)
###       #Pick the best stepc for each auction:
###       data.stepc.map <- pick.best.stepc(data, num_items=30)
###       write.stepc.map(data.stepc.map, sprintf('tables/basic/Basic_stepc_map_%s_%s', generator, relevant.auctions.name))
###       data.stepc <- data %>% inner_join(data.stepc.map, by=c("stepc", "auction"))
### #      create.table(data.stepc, generator, relevant.auctions.name, relevant.table.epsilon)
###       create.plots(data.stepc, generator, relevant.auctions.name)
###     }
###   }
###  create.summary.table()
  create.column.table('Rounds', bold_max=FALSE)
  create.column.table('Runtime', bold_max=FALSE)
  create.column.table('Price Degree', bold=FALSE)
  create.column.table('Price Terms', bold=FALSE)
  create.column.table('Efficiency')
  create.column.table('Revenue', bold=FALSE)
  create.column.table('Percent Cleared', rounding_precision=0)

  create.price_degree.plot()
  create.price_terms.plot()
  create.price_terms_personalized.plot()
  
  create.stepc_map.table()
}

# This block should run only if interactive mode
# Its purpose is to get the data and set variables for it:
if(interactive()) {
  for(generator in relevant.generators) {
    cat(sprintf("Reading Data for Generator %s...\n", generator))
    data <- read.data(generator, relevant.auctions.full, 'full')
    data.stepc.map <- pick.best.stepc(data, num_items=30)
    data.stepc <- data %>% inner_join(data.stepc.map, by=c("stepc", "auction"))
    assign(paste0("data.",generator), data)
    assign(paste0("data.",generator,".stepc.map"), data.stepc.map)
    assign(paste0("data.",generator,".stepc"), data.stepc)
    rm(data, data.stepc.map, data.stepc)
  }
}
cat('Done.')
#options(warn=2, error=traceback)
warnings()
