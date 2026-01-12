library(reshape2)
library(ggplot2)
library(ggpubr)
library(dplyr)
library(rstatix)

# --- 1. SETUP & DATA CLEANING ---

# Load Data
with_mask <- read.csv("C_with_mask.csv", header = T)$error_angle_deg
wout_mask <- read.csv("C_without_mask.csv", header = T)$error_angle_deg

conditions <- c("ctrl", "grad_perturb", "post_grad_perturb", "sudden_perturb", "post_sudden_perturb")

# Create Array
combined_data <- c(with_mask, wout_mask)
data_array <- array(combined_data, 
                    dim = c(40, 5, 2),
                    dimnames = list(time = 1:40, condition = conditions, mask_state = c("with_mask", "wout_mask")))

# Flatten to Dataframe
df_long <- melt(data_array, varnames = c("time", "condition", "mask_state"), value.name = "error_angle")
df_long$condition <- factor(df_long$condition, levels = conditions)

# --- 2. STATISTICAL CALCULATIONS ---

# TEST A: Mask Effect (With vs Without Mask)
stat_mask <- df_long %>%
  group_by(condition) %>%
  wilcox_test(error_angle ~ mask_state) %>%
  adjust_pvalue(method = "holm") %>%
  add_significance("p.adj") %>% 
  add_xy_position(x = "condition", dodge = 0.8) 

# TEST B: Interval Effect (Post-Grad vs Post-Sudden)
stat_intervals <- df_long %>%
  group_by(mask_state) %>% 
  wilcox_test(error_angle ~ condition) %>%
  adjust_pvalue(method = "holm") %>%
  add_significance("p.adj") %>%
  add_xy_position(x = "condition")

# --- 3. PLOTTING ---

# PLOT A: Mask Effect
p_mask <- ggplot(df_long, aes(x = condition, y = error_angle, fill = mask_state)) +
  geom_boxplot(alpha = 0.6, outlier.shape = NA, width = 0.8) + 
  geom_point(position = position_jitterdodge(jitter.width = 0.2, dodge.width = 0.8), 
             alpha = 0.3, size = 1) +
  stat_pvalue_manual(
    stat_mask, 
    label = "p.adj.signif", 
    tip.length = 0.01,
    hide.ns = F,
    inherit.aes = FALSE,
    y.position = max(df_long$error_angle, na.rm = TRUE) * 1.05
  ) +
  labs(title = "Mask Effect Analysis",
       subtitle = "Wilcoxon Tests (Holm-Corrected)",
       y = "Error Angle (deg)", x = "") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 25, hjust = 1),
        legend.position = "bottom")

# PLOT B: Interval Comparison
p_intervals <- ggplot(df_long, aes(x = condition, y = error_angle)) +
  geom_boxplot(alpha = 0.6, outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.2, size = 1) +
  facet_wrap(~mask_state) + 
  stat_pvalue_manual(
    stat_intervals, 
    label = "p.adj.signif",
    tip.length = 0.01,
    hide.ns = T,
    color = "black",
    inherit.aes = FALSE
  ) +
  labs(title = "Interval Analysis: Post-Grad vs Post-Sudden",
       subtitle = "Wilcoxon Tests (Holm-Corrected)",
       y = "Error Angle (deg)", x = "") +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 25, hjust = 1))

# --- 4. OUTPUT ---
print(p_mask)
print(p_intervals)

# Save
custom_save(p_mask, name = "result_mask_effect")
custom_save(p_intervals, name = "result_interval_comparison")