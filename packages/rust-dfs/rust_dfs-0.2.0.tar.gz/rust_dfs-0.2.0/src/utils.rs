use colored::*;

pub fn print_error(msg: &str) {
    let formatted_msg = format!("{}", msg);
    let formatted_msg_with_color = format!("{}", formatted_msg.black().bold());
    let bar = (0..formatted_msg.len()).map(|_| "=").collect::<String>();
    println!("{}", bar.red().bold());
    println!("{}", formatted_msg_with_color);
    println!("{}", bar.red().bold());
}

pub fn print_bar(msg: &str) {
    // I think this does the same thing
    // let title = "TODAY'S NEWS";
    // println!("{:-^30}", title);
    let total_len: i32 = 80;
    let msg_len: i32 = msg.len() as i32;

    let mid_idx = total_len / 2;
    let start_idx = mid_idx - (msg_len / 2) - 1;
    let stop_idx = mid_idx + (((msg_len as f32) / 2.0).ceil() as i32) + 1;

    let before = (0..start_idx).map(|_| "=").collect::<String>();
    let before_formatted = format!("{}", before.yellow().bold());

    let after = (stop_idx..total_len).map(|_| "=").collect::<String>();
    let after_formatted = format!("{}", after.yellow().bold());

    println!(
        "{} {} {}",
        before_formatted,
        msg.black().bold(),
        after_formatted
    );
}
