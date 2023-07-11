use std::{fs, path::Path};

use crate::Polycube;

#[derive(Debug)]
pub enum Error {
    Bincode(Box<bincode::ErrorKind>),
    Io(std::io::Error),
}

pub fn get_cache(path: &Path) -> Result<Vec<Polycube>, Error> {
    let bin = fs::read(path).map_err(Error::Io)?;
    let data: Vec<Polycube> = bincode::deserialize(&bin).map_err(Error::Bincode)?;
    Ok(data)
}

pub fn save_cache(path: &Path, data: &Vec<Polycube>) -> Result<(), Error> {
    let bin = bincode::serialize(&data).map_err(Error::Bincode)?;
    fs::write(path, bin).map_err(Error::Io)
}
