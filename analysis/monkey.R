# See: https://dlukes.github.io/monkey-patching-in-r.html

# Monkey patch the as.pdf.document() function in the latexpdf package so that it
# is silent on output.  We just change the system command below.

# See: https://stat.ethz.ch/R-manual/R-devel/library/base/html/system.html

latexpdf <- getNamespace("latexpdf")
unlockBinding("as.pdf.document", latexpdf)

####################################################################################################
# This part of the code is deliberately kept as similar to the original as possible, in order to
# make potential updates easier. 

# See: https://github.com/cran/latexpdf/blob/f92b6eb3c99b1263e30973ee4a17381653657094/R/util.R

contains <-
  function (pattern, text, ...)
  {
    hits <- regexpr(pattern, text, ...)
    hits >= 0
  }

# See: https://github.com/cran/latexpdf/blob/69a8065733df0a7a748803bd682996f119e83543/R/pdf.R

#' Coerce to PDF from Document
#'
#' Coerces to PDF from document. Makes a system call to 'pdflatex'. Extra arguments ignored.
#' @export
#' @describeIn as.pdf document method
#' @param stem the stem of a file name (no extension)
#' @param dir output directory
#' @param clean whether to delete system files after pdf creation
#' @return the output file path (invisible)

as.pdf.document <- function(
  x,
  stem = 'latexpdf-doc',
  dir='.',
  clean=TRUE,
  ignore.stdout=FALSE,
  ignore.stderr=FALSE,
  ...
){
  if(missing(stem))stop('a file stem (no extension) must be provided')
  if (contains('\\.pdf$',stem,ignore.case=TRUE)){
    warning('stripping .pdf from file stem ...')
    stem <- sub('\\.pdf$','',stem,ignore.case=TRUE)
  }
  outfile <- paste0(stem,'.tex')
  hopeful <- paste0(stem,'.pdf')
  outpath <- file.path(dir,outfile)
  expects <- file.path(dir,hopeful)
  writeLines(x,outpath)
  cmd <- paste0('pdflatex -output-directory=',dir,' ',outpath)
  result <- tryCatch(error = function(e)e, system(cmd, ignore.stdout=ignore.stdout, ignore.stderr=ignore.stderr))
  variants <- paste0(stem,c('.tex','.log','.aux','.out'))
  possibles <- file.path(dir,variants)
  actuals <- possibles[file.exists(possibles)]
  if(clean)file.remove(actuals)
  bad <- inherits(result,'try-error') || !file.exists(expects)
  if(bad) stop('could not make ', expects)
  invisible(expects)
}

# End pastiche of original latexpdf code.
####################################################################################################

#assignInNamespace("as.pdf.document", as.pdf.document, ns=latexpdf, envir=as.environment("package:latexpdf"))
latexpdf$as.pdf.document <- as.pdf.document
lockBinding("as.pdf.document", latexpdf)
