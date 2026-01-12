library(reshape2)
library(ggplot2)
library(ggpubr)
library(dplyr)

with_mask <- read.csv("C_with_mask.csv", header = T)$error_angle_deg
wout_mask <- read.csv("C_without_mask.csv", header = T)$error_angle_deg

conditions <- c("ctrl", "grad_perturb", "post_grad_perturb", "sudden_perturb", "post_sudden_perturb")

# Combine the two vectors into one long vector first
combined_data <- c(with_mask, wout_mask)

# Create a 3D array: [40 timepoints, 5 conditions, 2 mask_states]
data_array <- array(combined_data,
                    dim = c(40, 5, 2),
                    dimnames = list(
                      time = 1:40,
                      condition = conditions,
                      mask_state = c("with_mask", "wout_mask")
                    ))


# 1. Flatten the Array (The "Tidy" Step)
# This converts your 40x5x2 array into a long dataframe for analysis
df_long <- melt(data_array, 
                varnames = c("time", "condition", "mask_state"),
                value.name = "error_angle")

# Ensure factor levels are in the logical order provided (not alphabetical)
df_long$condition <- factor(df_long$condition, 
                            levels = unique(df_long$condition))

# 2. Compute Summary Statistics Separately
# Instead of appending to the array, we create a summary table
summary_stats <- df_long %>%
  group_by(condition, mask_state) %>%
  summarise(
    mean_error = mean(error_angle, na.rm = TRUE),
    sd_error = sd(error_angle, na.rm = TRUE),
    n = n(),
    se_error = sd_error / sqrt(n), # Standard Error
    .groups = 'drop'
  )

print("Summary Statistics:")
print(summary_stats)

# 3. Visualization with Statistical Analysis
# We compare "with_mask" vs "wout_mask" for each condition
p <- ggplot(df_long, aes(x = condition, y = error_angle, fill = mask_state)) +
  geom_boxplot(alpha = 0.6, outlier.shape = NA) +
  geom_point(position = position_jitterdodge(jitter.width = 0.2), 
             alpha = 0.3, size = 1) +
  #stat_summary(fun = mean, geom = "point", shape = 23, size = 3, 
  #             fill = "white", position = position_dodge(width = 0.75)) +
  stat_compare_means(aes(group = mask_state), 
                     method = "wilcox.test", 
                     label = "p.signif",       # Shows *, **, ns
                     label.y.npc = 0.95) +    # Places label at top
  labs(title = "Angular Error",
       subtitle = "Significance = Wilcoxon Test",
       y = "Error Angle (deg)",
       x = "Condition") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 25, hjust = 1), legend.position = "bottom") # Rotate x-labels

# Display Plot
print(p)

custom_save <- function(plt, folder = "", name = "", size=1, height = 1, width = 1.5, background = "white"){
  library(ggplot2)
  
  if(is.null(plt)){
    return("No plot to save\n")
  }
  
  #print(plt)
  ggsave(paste0(folder, name, ".png"), plt,
         height = height*2000*size,
         width = width*2000*size,
         units = "px",
         dpi = 500,
         create.dir = T ,
         bg = "white")
}

custom_save(p, name = "result_statistical_anal")

stat_results <- df_long %>%
  group_by(condition) %>%
  rstatix::wilcox_test(error_angle ~ mask_state) %>%
  rstatix::add_significance()

print("Test Results:")
print(stat_results)
