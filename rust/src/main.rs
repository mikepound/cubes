use std::time::Instant;

use clap::Parser;
use cubes::generate_polycubes;

// TODO: https://nnethercote.github.io/perf-book/title-page.html

/// Generates all polycubes (combinations of cubes) of size n.
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// The number of cubes within each polycube
    number: u8,

    /// Cache results to disk
    #[arg(long, default_value_t = false)]
    no_cache: bool,
}

fn main() {
    let args = Args::parse();

    // Start the timer
    let t1_start = Instant::now();

    let all_cubes = generate_polycubes(args.number, !args.no_cache);

    // Stop the timer
    let t1_stop = Instant::now();

    println!("Found {} unique polycube(s)", all_cubes.len());
    println!(
        "Elapsed time: {}s",
        t1_stop.duration_since(t1_start).as_secs()
    );
}
