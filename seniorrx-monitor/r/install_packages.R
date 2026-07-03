# Instala as dependencias R necessarias para renderizar reports/quarto/clinical_report.qmd
packages <- c("DBI", "RPostgres", "dplyr", "ggplot2", "gt", "quarto")

installed <- rownames(installed.packages())
to_install <- setdiff(packages, installed)

if (length(to_install) > 0) {
  install.packages(to_install, repos = "https://cloud.r-project.org")
}
