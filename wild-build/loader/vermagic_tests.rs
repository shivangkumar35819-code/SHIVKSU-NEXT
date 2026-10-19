use super::*;

fn fixture() -> Vec<u8> {
    let names = b"\0.shstrtab\0.modinfo\0.text\0";
    let modinfo = b"name=kernelsu\0vermagic=old SMP\0license=GPL\0";
    let mut bytes = vec![0u8; 512];
    bytes[..7].copy_from_slice(b"\x7fELF\x02\x01\x01");
    bytes[16..18].copy_from_slice(&1u16.to_le_bytes());
    bytes[18..20].copy_from_slice(&183u16.to_le_bytes());
    bytes[20..24].copy_from_slice(&1u32.to_le_bytes());
    bytes[40..48].copy_from_slice(&256u64.to_le_bytes());
    bytes[52..54].copy_from_slice(&64u16.to_le_bytes());
    bytes[58..60].copy_from_slice(&64u16.to_le_bytes());
    bytes[60..62].copy_from_slice(&4u16.to_le_bytes());
    bytes[62..64].copy_from_slice(&1u16.to_le_bytes());
    bytes[64..64 + names.len()].copy_from_slice(names);
    bytes[96..96 + modinfo.len()].copy_from_slice(modinfo);
    bytes[160..164].copy_from_slice(&[1, 2, 3, 4]);
    for (index, name, kind, offset, size) in [
        (1, 1u32, 3u32, 64u64, names.len() as u64),
        (2, 11, 1, 96, modinfo.len() as u64),
        (3, 20, 1, 160, 4),
    ] {
        let header = 256 + index * 64;
        bytes[header..header + 4].copy_from_slice(&name.to_le_bytes());
        bytes[header + 4..header + 8].copy_from_slice(&kind.to_le_bytes());
        write_elf64_word(&mut bytes, header + 24, offset, true).unwrap();
        write_elf64_word(&mut bytes, header + 32, size, true).unwrap();
        write_elf64_word(&mut bytes, header + 48, 1, true).unwrap();
    }
    bytes
}

#[test]
fn only_this_modules_latest_mismatch_is_used() {
    let logs = "kernelsu: version magic 'old' should be 'first'\n\
        3,2,0,-;other: version magic 'old' should be 'wrong'\n\
        3,3,0,-;kernelsu: version magic 'old' should be 'required SMP'\n";
    assert_eq!(extract_required_vermagic(logs).as_deref(), Some("required SMP"));
    assert_eq!(extract_required_vermagic("other: version magic 'a' should be 'b'"), None);
    assert_eq!(extract_required_vermagic("kernelsu: version magic 'bad"), None);
    assert_eq!(extract_required_vermagic("kernelsu: version magic 'a' should be ''"), None);
}

#[test]
fn replacement_preserves_code_and_other_metadata() {
    let mut bytes = fixture();
    let original = bytes.clone();
    for required in ["6.6.118-android15-8-device SMP preempt mod_unload modversions aarch64", "short"] {
        replace_module_vermagic(&mut bytes, required).unwrap();
        let elf = Elf::parse(&bytes).unwrap();
        let section = elf.section_headers.iter().find(|s| elf.shdr_strtab.get_at(s.sh_name) == Some(".modinfo")).unwrap();
        let data = &bytes[section.sh_offset as usize..(section.sh_offset + section.sh_size) as usize];
        let entries: Vec<_> = data.split(|byte| *byte == 0).collect();
        assert!(entries.contains(&b"name=kernelsu".as_slice()));
        assert!(entries.contains(&b"license=GPL".as_slice()));
        assert!(entries.contains(&format!("vermagic={required}").as_bytes()));
        assert_eq!(&bytes[160..164], &original[160..164]);
        assert_eq!(&bytes[256..384], &original[256..384]);
        assert_eq!(&bytes[448..512], &original[448..512]);
    }
}

#[test]
fn malformed_modules_and_injected_strings_are_rejected() {
    assert!(replace_module_vermagic(&mut vec![0; 64], "required").is_err());
    for required in ["", "bad\0name=wrong", "bad\nline"] {
        assert!(replace_module_vermagic(&mut fixture(), required).is_err());
    }
    let mut bytes = fixture();
    bytes[16..18].copy_from_slice(&2u16.to_le_bytes());
    assert!(replace_module_vermagic(&mut bytes, "required").is_err());
    assert!(align_up(usize::MAX, 8).is_err());
    assert!(align_up(8, 3).is_err());
}
