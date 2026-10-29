LD_PRELOAD= ./trace_reader /ramdisk/delphi-trace-reader_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa > trace-job.txt 2>&1 & delphi_trace_job=$!; echo OS31cd3ae8b2:$?:END
