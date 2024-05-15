library(dplyr)
library(jtools)
library(magrittr)
library(stringr)

# Find the average salary per experience level.

data <- read.csv(Sys.getenv('jobscryer_data_path'))

get_salaries <- function(data) {
  salary_range <- str_match(data$salary, ".* (\\d+)K - (\\d+)K .*")
  data <- data %>% mutate(salary_min = as.numeric(salary_range[,2])*1000,
                          salary_max = as.numeric(salary_range[,3])*1000)
  return(data)
}

find_mode <- function(x) {
  ux <- na.omit(unique(x))  # Remove NAs (nulls) and get unique values
  tab <- tabulate(match(x, ux))  # Count occurrences of each value
  ux[tab == max(tab)]  # Return the value(s) with the highest frequency
}

data <- get_salaries(data)

avg_salaries <- data %>%
  group_by(exp_level) %>%
  summarize(avg_salary_min = mean(salary_min, na.rm = TRUE), #na.rm skips nulls
            avg_salary_max = mean(salary_max, na.rm = TRUE),
            mode_salary_min = find_mode(salary_min),
            mode_salary_max = find_mode(salary_max)
            )

sorted_salaries <- avg_salaries %>% arrange(avg_salary_max)
