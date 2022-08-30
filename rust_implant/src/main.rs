use std::io;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut url = String::new();
    io::stdin().read_line(&mut url)?;

    let resp = reqwest::get(url)
        .await?
        .text()
        .await?;
    println!("{:?}", resp);
    Ok(())
}